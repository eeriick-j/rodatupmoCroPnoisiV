"""Genera los dos extras de P4: anonimización y flujo direccional.

Entradas:
    detecciones.csv      -> cajas y tracking de la Tarea 1
    video_tarea1.mp4     -> vídeo anotado de la Tarea 1

Salidas:
    video_anonimizado.mp4
    flujo_direcciones.csv
    flujo_direcciones_resumen.csv
    flujo_direcciones.png
"""

from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
CSV = BASE / "detecciones.csv"
VIDEO = BASE / "video_tarea1.mp4"

VIDEO_OUT = BASE / "video_anonimizado.mp4"
FLUJO_CSV = BASE / "flujo_direcciones.csv"
FLUJO_RESUMEN = BASE / "flujo_direcciones_resumen.csv"
FLUJO_PNG = BASE / "flujo_direcciones.png"

# Las coordenadas del CSV están en el vídeo original 1920x1080.
ORIGEN_W, ORIGEN_H = 1920, 1080

# Un track se considera válido para el flujo si tiene suficiente recorrido.
MIN_DETECCIONES = 5
MIN_DESPLAZAMIENTO_PX = 20.0

CLASS_ORDER = ["coche", "persona", "camion", "autobus", "moto"]
DIR_ORDER = ["izquierda", "derecha", "arriba", "abajo"]


def pixelar(frame, x1, y1, x2, y2, bloques=10):
    """Sustituye la región por una versión pixelada."""
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(frame.shape[1], int(x2))
    y2 = min(frame.shape[0], int(y2))

    if x2 - x1 < 3 or y2 - y1 < 3:
        return

    roi = frame[y1:y2, x1:x2]
    h, w = roi.shape[:2]
    small_w = max(1, w // bloques)
    small_h = max(1, h // bloques)
    pequena = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
    pixelada = cv2.resize(pequena, (w, h), interpolation=cv2.INTER_NEAREST)
    frame[y1:y2, x1:x2] = pixelada


def anonimizar(df):
    cap = cv2.VideoCapture(str(VIDEO))
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir {VIDEO}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(VIDEO_OUT), fourcc, fps, (width, height))
    if not out.isOpened():
        raise RuntimeError(f"No se pudo crear {VIDEO_OUT}")

    sx = width / ORIGEN_W
    sy = height / ORIGEN_H

    por_fotograma = {}
    for row in df.itertuples(index=False):
        por_fotograma.setdefault(int(row.fotograma), []).append(
            (int(row.x1), int(row.y1), int(row.x2), int(row.y2))
        )

    frame_number = 0
    cajas_difuminadas = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame_number += 1
        for x1, y1, x2, y2 in por_fotograma.get(frame_number, []):
            # Pequeño margen para incluir el borde de la caja.
            margen = 4
            pixelar(
                frame,
                x1 * sx - margen,
                y1 * sy - margen,
                x2 * sx + margen,
                y2 * sy + margen,
            )
            cajas_difuminadas += 1

        cv2.rectangle(frame, (10, 10), (255, 45), (0, 0, 0), -1)
        cv2.putText(
            frame,
            "ANONIMIZADO",
            (18, 36),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        out.write(frame)
        if frame_number % 250 == 0:
            print(f"Anonimizando {frame_number}/{total}", end="\r")

    cap.release()
    out.release()
    print(f"\nVídeo anonimizado: {VIDEO_OUT}")
    print(f"Fotogramas: {frame_number} | Cajas pixeladas: {cajas_difuminadas}")


def calcular_flujo(df):
    filas = []
    for (track_id, clase), grupo in df.groupby(
        ["identificador_tracking", "tipo_objeto"], sort=False
    ):
        grupo = grupo.sort_values("fotograma")
        if len(grupo) < 2:
            continue

        primero = grupo.iloc[0]
        ultimo = grupo.iloc[-1]

        x_ini = (float(primero.x1) + float(primero.x2)) / 2.0
        y_ini = (float(primero.y1) + float(primero.y2)) / 2.0
        x_fin = (float(ultimo.x1) + float(ultimo.x2)) / 2.0
        y_fin = (float(ultimo.y1) + float(ultimo.y2)) / 2.0

        dx = x_fin - x_ini
        dy = y_fin - y_ini
        distancia = float(np.hypot(dx, dy))

        if distancia < MIN_DESPLAZAMIENTO_PX:
            direccion = "sin_direccion"
        elif abs(dx) >= abs(dy):
            direccion = "derecha" if dx > 0 else "izquierda"
        else:
            direccion = "abajo" if dy > 0 else "arriba"

        valido = len(grupo) >= MIN_DETECCIONES and distancia >= MIN_DESPLAZAMIENTO_PX

        if len(grupo) < MIN_DETECCIONES:
            motivo = "pocas_detecciones"
        elif distancia < MIN_DESPLAZAMIENTO_PX:
            motivo = "desplazamiento_pequeno"
        else:
            motivo = ""

        filas.append(
            {
                "identificador_tracking": int(track_id),
                "tipo_objeto": clase,
                "fotograma_inicio": int(primero.fotograma),
                "fotograma_fin": int(ultimo.fotograma),
                "num_detecciones": int(len(grupo)),
                "x_inicio": round(x_ini, 1),
                "y_inicio": round(y_ini, 1),
                "x_fin": round(x_fin, 1),
                "y_fin": round(y_fin, 1),
                "dx": round(dx, 1),
                "dy": round(dy, 1),
                "distancia_px": round(distancia, 1),
                "direccion": direccion,
                "valido": int(valido),
                "motivo_descarte": motivo,
            }
        )

    flujo = pd.DataFrame(filas)
    flujo = flujo.sort_values(["tipo_objeto", "identificador_tracking"]).reset_index(
        drop=True
    )
    flujo.to_csv(FLUJO_CSV, index=False, encoding="utf-8")

    validos = flujo[flujo["valido"] == 1]
    resumen = (
        validos.groupby(["tipo_objeto", "direccion"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=DIR_ORDER, fill_value=0)
    )

    totales = flujo.groupby("tipo_objeto").size().rename("total_tracks")
    validos_por_clase = validos.groupby("tipo_objeto").size().rename("tracks_validos")
    resumen = resumen.join(totales).join(validos_por_clase, how="outer").fillna(0)
    resumen["tracks_descartados"] = resumen["total_tracks"] - resumen["tracks_validos"]
    resumen = resumen.astype(int)

    orden = [c for c in CLASS_ORDER if c in resumen.index]
    orden += [c for c in resumen.index if c not in orden]
    resumen = resumen.loc[orden]
    resumen.to_csv(FLUJO_RESUMEN, encoding="utf-8")

    # Gráfica de barras agrupadas por clase y dirección.
    plot = resumen[DIR_ORDER]
    ax = plot.plot(
        kind="bar",
        figsize=(10, 5),
        color=["#4C72B0", "#DD8452", "#55A868", "#C44E52"],
        width=0.8,
    )
    ax.set_title("Flujo direccional por clase (tracks válidos)")
    ax.set_xlabel("Clase")
    ax.set_ylabel("Número de tracks")
    ax.grid(axis="y", alpha=0.3)
    ax.legend(title="Dirección", ncol=4, loc="upper right")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(FLUJO_PNG, dpi=160, bbox_inches="tight")
    plt.close()

    print(f"Flujo por track: {FLUJO_CSV}")
    print(f"Resumen: {FLUJO_RESUMEN}")
    print(f"Gráfica: {FLUJO_PNG}")
    print(f"Tracks totales: {len(flujo)} | válidos: {len(validos)}")


def main():
    df = pd.read_csv(CSV)
    anonimizar(df)
    calcular_flujo(df)


if __name__ == "__main__":
    main()
