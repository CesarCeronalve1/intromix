import random
from pydub import AudioSegment

def efectos(audio: AudioSegment) -> AudioSegment:
    """
    Aplica una transición DJ SOLO al final del clip
    y SIEMPRE termina con un low fade suave.
    """

    dur = len(audio)
    if dur < 4000:
        return audio.fade_out(500)

    # Duración del fragmento final
    tail_ms = random.randint(1000, 1400)

    cuerpo = audio[:-tail_ms]
    tail = audio[-tail_ms:]

    efecto = random.choice([
        # "none",
        "tape_stop",
        "echo_tail",
        "reverb_tail",
        "repeat_tail",
         "micro_cut",
        # "reverse_hit"
    ])

    #1: tapestop efecto
    if efecto == "tape_stop":
        # Duración total del efecto (ms)
        duracion_efecto = min(len(tail), 1500)  # Máximo 1.5 segundos
        
        # Dividir en 3 partes con diferentes velocidades
        parte1 = tail[:duracion_efecto//3]
        parte2 = tail[duracion_efecto//3:2*duracion_efecto//3]
        parte3 = tail[2*duracion_efecto//3:duracion_efecto]
        resto = tail[duracion_efecto:]
        
        # Aplicar reducción gradual
        parte1 = parte1._spawn(parte1.raw_data, overrides={"frame_rate": int(parte1.frame_rate * 0.90)}).set_frame_rate(tail.frame_rate)
        parte2 = parte2._spawn(parte2.raw_data, overrides={"frame_rate": int(parte2.frame_rate * 0.85)}).set_frame_rate(tail.frame_rate)
        parte3 = parte3._spawn(parte3.raw_data, overrides={"frame_rate": int(parte3.frame_rate * 0.80)}).set_frame_rate(tail.frame_rate)
        
        # Recombinar
        tail = parte1 + parte2 + parte3 + resto
        
        # Fade out final
        tail = tail.fade_out(300)
        
        print("efecto Tape stop gradual aplicado")



    elif efecto == "echo_tail":
        tail = tail.overlay(tail - 6, position=180)
        tail = tail.overlay(tail - 12, position=360)
        print("efecto tail")

    # 🏟️ 3. Reverb cola
    elif efecto == "reverb_tail":
        for d, vol in [(120, -6), (240, -10), (360, -14)]:
            tail = tail.overlay(tail + vol, position=d)
        print("efecto reberb tail")


    # 🔁 4. Repetición rítmica x3
    elif efecto == "repeat_tail":
        slice_ms = random.choice([200, 300, 500])
        # slice_ms = random.choice([120, 160, 200])
        loop = tail[-slice_ms:]
        tail = loop + loop + loop
        print("efecto repeticion ritmica x3")


    # ✂️ 5. Micro cortes rítmicos (muy DJ)
    elif efecto == "micro_cut":
        slice_ms = random.choice([80, 100])
        cut = tail[-slice_ms:]
        tail = cut + AudioSegment.silent(40) + cut
        print("micro con cortes ritmicos")


    # 🔄 6. Reverse hit corto
    elif efecto == "reverse_hit":
        partes = []
        # desaceleración progresiva
        for speed, vol in [(0.85, -2), (0.7, -6), (0.55, -12)]:
            fragmento = tail.speedup(playback_speed=speed)
            fragmento = fragmento + vol
            partes.append(fragmento[:len(tail)//3])

        tail = sum(partes, AudioSegment.silent(0))
        tail = tail.fade_out(600)


    # 🎧 LOW FADE FINAL (SIEMPRE)
    tail = tail.fade_out(700)
    # print("El fade")


    return cuerpo + tail
