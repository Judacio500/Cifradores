import streamlit as st
import hashlib
import time
import sys
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.exceptions import InvalidSignature, InvalidTag

st.set_page_config(layout="wide", page_title="Cripto-Laboratorio")

st.markdown(
    """
    <style>
        ul[data-testid="stSidebarNavItems"] li:nth-child(1) {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def renderizar_ficha(s_entradas, s_componentes, s_secreto, s_salidas, s_propiedad, d_recursos, s_condiciones):
    st.markdown("<h4 style='color: #cc0000;'>Ficha Técnica del Mecanismo</h4>", unsafe_allow_html=True)
    st.markdown(f"**Entradas:** {s_entradas}<br>**Componentes Criptográficos:** {s_componentes}<br>**Secreto y Público:** {s_secreto}<br>**Salidas:** {s_salidas}<br>**Propiedad Proporcionada:** {s_propiedad}<br>**Condiciones de Uso:** {s_condiciones}", unsafe_allow_html=True)
    st.caption(f"**Recursos Computacionales:** Tiempo de ejecución: {d_recursos.get('tiempo', 0):.6f}s | Memoria en objeto Python: {d_recursos.get('memoria', 0)} bytes. (Atención: La memoria medida desde Python puede no incluir todas las asignaciones de las bibliotecas nativas).")

if "vista_actual_cripto" not in st.session_state:
    st.session_state.vista_actual_cripto = 0
if "claves_rsa_alice" not in st.session_state:
    st.session_state.claves_rsa_alice = rsa.generate_private_key(public_exponent=65537, key_size=2048)
if "claves_rsa_bob" not in st.session_state:
    st.session_state.claves_rsa_bob = rsa.generate_private_key(public_exponent=65537, key_size=2048)
if "llave_simetrica" not in st.session_state:
    st.session_state.llave_simetrica = os.urandom(32)
if "nonces_registrados" not in st.session_state:
    st.session_state.nonces_registrados = set()
if "ca_privada" not in st.session_state:
    st.session_state.ca_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
if "ca_falsa" not in st.session_state:
    st.session_state.ca_falsa = rsa.generate_private_key(public_exponent=65537, key_size=2048)

with st.sidebar:
    st.markdown("<h3 style='color: #cc0000;'>Menú Principal</h3>", unsafe_allow_html=True)
    st.write("")
    if st.button("Hash Criptográfico", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 0
    if st.button("Construcción Esponja", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 1
    if st.button("Cifrado por Bloques", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 2
    if st.button("Cifrado por Flujo", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 3
    if st.button("MAC y Cifrado Autenticado", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 4
    if st.button("Derivación de Claves (KDF)", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 5
    if st.button("Clave Pública", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 6
    if st.button("Firmas Digitales", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 7
    if st.button("Intercambio de Claves", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 8
    if st.button("Infraestructura PKI", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 9
    if st.button("Conclusiones y Tabla", type="primary", use_container_width=True): st.session_state.vista_actual_cripto = 10

st.markdown("<h1 style='text-align: center; color: #cc0000; font-family: Arial, sans-serif;'>LABORATORIO CRIPTOGRÁFICO</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555555; font-family: Arial, sans-serif;'>Análisis de Primitivas y Vectores de Ataque</h4>", unsafe_allow_html=True)
st.divider()

if st.session_state.vista_actual_cripto != 10:
    col_alice, col_eve, col_bob = st.columns(3)

match st.session_state.vista_actual_cripto:
    case 0:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            s_mensaje = st.text_input("Contraseña Débil", value="123456")
            if st.button("Calcular Huella", type="primary", use_container_width=True):
                t0 = time.perf_counter()
                s_huella = hashlib.sha256(s_mensaje.encode()).hexdigest()
                tf = time.perf_counter()
                st.session_state.canal_0 = s_huella
                st.session_state.recursos_0 = {"tiempo": tf-t0, "memoria": sys.getsizeof(s_huella)}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante Simulador)</h4>", unsafe_allow_html=True)
            if "canal_0" in st.session_state:
                st.info(f"Interceptado en el canal: {st.session_state.canal_0[:15]}...")
                s_ataque = st.selectbox("Laboratorio de Eve", ["Observar", "Probar un diccionario pequeño"])
                if s_ataque == "Probar un diccionario pequeño":
                    l_diccionario = ["admin", "root", "123456", "password", "qwerty"]
                    b_exito = False
                    for s_palabra in l_diccionario:
                        if hashlib.sha256(s_palabra.encode()).hexdigest() == st.session_state.canal_0:
                            st.error(f"Aprendizaje: Recuperar por diccionario NO equivale a descifrar. Contraseña deducida: {s_palabra}")
                            b_exito = True
                            break
                    if not b_exito:
                        st.warning("El ataque de diccionario falló.")
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_0" in st.session_state:
                st.success(f"Huella almacenada: {st.session_state.canal_0[:15]}...")
                st.write("Bob acepta el hash para validación futura.")
        st.divider()
        if "recursos_0" in st.session_state:
            renderizar_ficha("Contraseña o mensaje en texto plano", "Ninguno externo, solo el algoritmo SHA-256", "Proteger: El mensaje original. Público: La huella resultante", "Hash (Huella) de longitud fija", "Integridad, Resistencia a preimagen y colisiones", st.session_state.recursos_0, "Una contraseña débil sigue siendo vulnerable a ataques por diccionario o fuerza bruta. No usar hashes simples para contraseñas.")

    case 1:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            s_mensaje = st.text_input("Datos Semilla", value="SemillaSistemaBase")
            n_longitud = st.number_input("Longitud de Salida (Bytes)", min_value=16, max_value=256, value=32, step=16)
            if st.button("Generar XOF", type="primary", use_container_width=True):
                t0 = time.perf_counter()
                o_shake = hashlib.shake_256(s_mensaje.encode())
                b_salida = o_shake.digest(n_longitud)
                tf = time.perf_counter()
                st.session_state.canal_1 = b_salida
                st.session_state.recursos_1 = {"tiempo": tf-t0, "memoria": sys.getsizeof(b_salida)}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante)</h4>", unsafe_allow_html=True)
            if "canal_1" in st.session_state:
                st.info(f"Salida expandida en tránsito: {st.session_state.canal_1.hex()[:20]}...")
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_1" in st.session_state:
                st.success(f"Bob recibe una cadena pseudoaleatoria de la longitud solicitada.")
        st.divider()
        if "recursos_1" in st.session_state:
            renderizar_ficha("Mensaje arbitrario, Longitud deseada", "Construcción Esponja (SHAKE256)", "Proteger: Semilla interna. Público: Salida XOF extendida", "Flujo de bytes de longitud dinámica", "Flexibilidad criptográfica, simulación de flujos", st.session_state.recursos_1, "Evitar colisiones requiriendo longitudes mayores a 32 bytes (256 bits).")

    case 2:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            s_mensaje = st.text_input("Datos Críticos", value="PAGAR $0100 A BOB")
            if st.button("Cifrar AES-CTR", type="primary", use_container_width=True):
                b_nonce = os.urandom(16)
                o_cifrador = Cipher(algorithms.AES(st.session_state.llave_simetrica), modes.CTR(b_nonce))
                o_enc = o_cifrador.encryptor()
                t0 = time.perf_counter()
                b_cifrado = o_enc.update(s_mensaje.encode()) + o_enc.finalize()
                tf = time.perf_counter()
                st.session_state.canal_2 = {"nonce": b_nonce, "cifrado": b_cifrado}
                st.session_state.recursos_2 = {"tiempo": tf-t0, "memoria": sys.getsizeof(b_cifrado)}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante)</h4>", unsafe_allow_html=True)
            if "canal_2" in st.session_state:
                d_paquete = st.session_state.canal_2
                s_ataque = st.selectbox("Laboratorio de Eve", ["Observar", "Alterar bytes (Cifrado sin Autenticación)"])
                if s_ataque == "Alterar bytes (Cifrado sin Autenticación)":
                    ba_cifrado = bytearray(d_paquete["cifrado"])
                    ba_cifrado[7] = ba_cifrado[7] ^ ord('0') ^ ord('9')
                    st.session_state.canal_2_mod = {"nonce": d_paquete["nonce"], "cifrado": bytes(ba_cifrado)}
                    st.error("Eve inyectó manipulación de bits en el texto cifrado.")
                else:
                    st.session_state.canal_2_mod = d_paquete
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_2_mod" in st.session_state:
                d_rx = st.session_state.canal_2_mod
                o_descifrador = Cipher(algorithms.AES(st.session_state.llave_simetrica), modes.CTR(d_rx["nonce"]))
                o_dec = o_descifrador.decryptor()
                b_descifrado = o_dec.update(d_rx["cifrado"]) + o_dec.finalize()
                st.warning(f"Bob acepta el descifrado resultante: {b_descifrado.decode(errors='replace')}")
                st.error("Aprendizaje: El cifrado por sí solo no garantiza detección de modificaciones.")
        st.divider()
        if "recursos_2" in st.session_state:
            renderizar_ficha("Mensaje, Secreto Compartido", "Llave Simétrica AES, Nonce, Contador Interno", "Proteger: Llave Simétrica. Público: Texto cifrado, Nonce", "Texto cifrado", "Exclusivamente Confidencialidad", st.session_state.recursos_2, "Reutilizar el Nonce destruye toda la seguridad. Sujeto a vulnerabilidad de maleabilidad.")

    case 3:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            s_mensaje = st.text_input("Comando Operativo", value="INICIAR_TRANSFERENCIA")
            if st.button("Cifrar ChaCha20", type="primary", use_container_width=True):
                b_nonce = os.urandom(16)
                o_cifrador = Cipher(algorithms.ChaCha20(st.session_state.llave_simetrica, b_nonce), modes.Mode())
                o_enc = o_cifrador.encryptor()
                t0 = time.perf_counter()
                b_cifrado = o_enc.update(s_mensaje.encode())
                tf = time.perf_counter()
                st.session_state.canal_3 = {"nonce": b_nonce, "cifrado": b_cifrado}
                st.session_state.recursos_3 = {"tiempo": tf-t0, "memoria": sys.getsizeof(b_cifrado)}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante)</h4>", unsafe_allow_html=True)
            if "canal_3" in st.session_state:
                s_ataque = st.selectbox("Laboratorio de Eve", ["Observar", "Reenviar un mensaje válido"])
                if s_ataque == "Reenviar un mensaje válido":
                    st.session_state.canal_3_mod = st.session_state.canal_3
                    st.error("Eve retransmite el paquete completo capturado previamente (Replay Attack).")
                else:
                    st.session_state.canal_3_mod = st.session_state.canal_3
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_3_mod" in st.session_state:
                d_rx = st.session_state.canal_3_mod
                if d_rx["nonce"] in st.session_state.nonces_registrados:
                    st.error("Rechazado. Aprendizaje: La autenticación necesita controles adicionales como rastreo de Nonces o Marcas de Tiempo para impedir repeticiones.")
                else:
                    st.session_state.nonces_registrados.add(d_rx["nonce"])
                    o_descifrador = Cipher(algorithms.ChaCha20(st.session_state.llave_simetrica, d_rx["nonce"]), modes.Mode())
                    o_dec = o_descifrador.decryptor()
                    b_descifrado = o_dec.update(d_rx["cifrado"])
                    st.success(f"Aceptado y ejecutado: {b_descifrado.decode(errors='replace')}")
        st.divider()
        if "recursos_3" in st.session_state:
            renderizar_ficha("Mensaje, Secreto Compartido", "Llave ChaCha20, Nonce", "Proteger: Llave. Público: Texto cifrado, Nonce", "Texto cifrado del flujo", "Confidencialidad", st.session_state.recursos