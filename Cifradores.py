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
            renderizar_ficha("Mensaje, Secreto Compartido", "Llave ChaCha20, Nonce", "Proteger: Llave. Público: Texto cifrado, Nonce", "Texto cifrado del flujo", "Confidencialidad", st.session_state.recursos_3, "Requiere control estricto del estado de red para mitigar reenvíos.")

    case 4:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            s_tipo = st.radio("Mecanismo", ["HMAC", "AES-GCM"])
            s_mensaje = st.text_input("Carga Crítica", value="CONFIGURACION_ROOT")
            if st.button("Ejecutar Operación", type="primary", use_container_width=True):
                t0 = time.perf_counter()
                if s_tipo == "HMAC":
                    o_h = hmac.HMAC(st.session_state.llave_simetrica, hashes.SHA256())
                    o_h.update(s_mensaje.encode())
                    b_tag = o_h.finalize()
                    tf = time.perf_counter()
                    st.session_state.canal_4 = {"tipo": "HMAC", "msg": s_mensaje.encode(), "tag": b_tag}
                    st.session_state.recursos_4 = {"tiempo": tf-t0, "memoria": sys.getsizeof(b_tag)}
                else:
                    b_iv = os.urandom(12)
                    o_cifrador = Cipher(algorithms.AES(st.session_state.llave_simetrica), modes.GCM(b_iv))
                    o_enc = o_cifrador.encryptor()
                    o_enc.authenticate_additional_data(b"DATOS_ASOCIADOS")
                    b_cif = o_enc.update(s_mensaje.encode()) + o_enc.finalize()
                    tf = time.perf_counter()
                    st.session_state.canal_4 = {"tipo": "GCM", "iv": b_iv, "cifrado": b_cif, "tag": o_enc.tag, "ad": b"DATOS_ASOCIADOS"}
                    st.session_state.recursos_4 = {"tiempo": tf-t0, "memoria": sys.getsizeof(b_cif)}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante)</h4>", unsafe_allow_html=True)
            if "canal_4" in st.session_state:
                s_ataque = st.selectbox("Laboratorio de Eve", ["Observar", "Modificar Mensaje sin conocer llave (HMAC)", "Alterar cifrado o datos asociados (AES-GCM)"])
                d_mod = st.session_state.canal_4.copy()
                if s_ataque == "Modificar Mensaje sin conocer llave (HMAC)" and d_mod["tipo"] == "HMAC":
                    d_mod["msg"] = b"CONFIGURACION_EVE"
                    st.error("Mensaje alterado pero la etiqueta se conserva igual.")
                elif s_ataque == "Alterar cifrado o datos asociados (AES-GCM)" and d_mod["tipo"] == "GCM":
                    ba_c = bytearray(d_mod["cifrado"])
                    if len(ba_c) > 0: ba_c[0] ^= 0xFF
                    d_mod["cifrado"] = bytes(ba_c)
                    d_mod["ad"] = b"ASOCIADOS_ALTERADOS"
                    st.error("Se inyectaron bits corruptos en el texto cifrado y los datos adicionales.")
                st.session_state.canal_4_mod = d_mod
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_4_mod" in st.session_state:
                d_rx = st.session_state.canal_4_mod
                if d_rx["tipo"] == "HMAC":
                    o_h = hmac.HMAC(st.session_state.llave_simetrica, hashes.SHA256())
                    o_h.update(d_rx["msg"])
                    try:
                        o_h.verify(d_rx["tag"])
                        st.success("Bob verifica: El código MAC es válido.")
                    except InvalidSignature:
                        st.error("Aprendizaje: La etiqueta original deja de ser válida si se manipula el texto.")
                else:
                    o_descifrador = Cipher(algorithms.AES(st.session_state.llave_simetrica), modes.GCM(d_rx["iv"], d_rx["tag"]))
                    o_dec = o_descifrador.decryptor()
                    o_dec.authenticate_additional_data(d_rx["ad"])
                    try:
                        b_desc = o_dec.update(d_rx["cifrado"]) + o_dec.finalize()
                        st.success(f"GCM Autenticado correctamente: {b_desc.decode(errors='replace')}")
                    except InvalidTag:
                        st.error("Aprendizaje: La verificación falla ante cualquier mínimo cambio en el cifrado o sus datos asociados.")
        st.divider()
        if "recursos_4" in st.session_state:
            renderizar_ficha("Mensaje o Texto Cifrado, Datos Asociados", "Llaves Simétricas, IV, Etiqueta MAC", "Proteger: Llaves. Público: Etiqueta, Texto Cifrado, Datos Adicionales", "Etiqueta MAC o Texto Cifrado con Etiqueta embebida", "Autenticación, Integridad y (en GCM) Confidencialidad", st.session_state.recursos_4, "Jamás reutilizar el IV bajo la misma llave en AES-GCM; colapsaría la autenticación.")

    case 5:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            s_pwd = st.text_input("Contraseña Maestra", value="ClaveMaestra")
            if st.button("Derivar Claves Simétricas", type="primary", use_container_width=True):
                b_sal = os.urandom(16)
                t0 = time.perf_counter()
                b_sha = hashlib.sha256(s_pwd.encode()).digest()
                t1 = time.perf_counter()
                o_scrypt = Scrypt(salt=b_sal, length=32, n=2**14, r=8, p=1)
                b_scrypt = o_scrypt.derive(s_pwd.encode())
                t2 = time.perf_counter()
                st.session_state.canal_5 = {"sal": b_sal, "pwd": s_pwd, "t_sha": t1-t0, "t_scrypt": t2-t1}
                st.session_state.recursos_5 = {"tiempo": t2-t0, "memoria": sys.getsizeof(b_scrypt)}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante)</h4>", unsafe_allow_html=True)
            if "canal_5" in st.session_state:
                st.info(f"Observa la derivación. Sal utilizada: {st.session_state.canal_5['sal'].hex()[:10]}")
                if st.button("Comparar Intentos", type="secondary"):
                    t_s = st.session_state.canal_5['t_sha']
                    t_sc = st.session_state.canal_5['t_scrypt']
                    st.warning(f"Costos para Eve (1 millón de iteraciones de diccionario directo en SHA256): {t_s * 1000000:.2f} segundos")
                    st.success(f"Costos para Eve (1 millón de iteraciones simuladas en Scrypt): {t_sc * 1000000:.2f} segundos")
                    st.error("Aprendizaje: Los parámetros de costo afectan el trabajo de cada intento, haciéndolo computacionalmente inviable.")
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_5" in st.session_state:
                st.write("Bob deriva la misma llave gracias a la Sal que se transmitió en claro.")
        st.divider()
        if "recursos_5" in st.session_state:
            renderizar_ficha("Contraseña Base, Sal Aleatoria", "Funciones KDF (Scrypt, PBKDF2), Parámetros de Costo Memoria/CPU", "Proteger: Contraseña origen, Clave final. Público: Parámetros y Sal", "Llave simétrica de tamaño estricto", "Establecimiento de claves seguro", st.session_state.recursos_5, "Evitar sal estática; ajustar parámetros de costo para que cada derivación consuma más de 100ms.")

    case 6:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            s_mensaje = st.text_input("Secreto hacia Bob", value="Coordenadas del Sector 4")
            if st.button("Cifrar con Pública de Bob", type="primary", use_container_width=True):
                t0 = time.perf_counter()
                b_cifrado = st.session_state.claves_rsa_bob.public_key().encrypt(s_mensaje.encode(), padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
                tf = time.perf_counter()
                st.session_state.canal_6 = b_cifrado
                st.session_state.recursos_6 = {"tiempo": tf-t0, "memoria": sys.getsizeof(b_cifrado)}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante)</h4>", unsafe_allow_html=True)
            if "canal_6" in st.session_state:
                st.info(f"Cifrado capturado: {st.session_state.canal_6.hex()[:20]}...")
                st.error("Eve es incapaz de factorizar la llave privada o revertir el texto asimétrico.")
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_6" in st.session_state:
                b_descifrado = st.session_state.claves_rsa_bob.decrypt(st.session_state.canal_6, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
                st.success(f"Bob descifra exitosamente: {b_descifrado.decode()}")
        st.divider()
        if "recursos_6" in st.session_state:
            renderizar_ficha("Mensaje Corto, Llave Pública", "Matemática RSA, Relleno OAEP", "Proteger: Llave Privada y Plaintext. Público: Llave Pública, Cifrado", "Texto cifrado asimétrico", "Confidencialidad Asimétrica", st.session_state.recursos_6, "El tamaño del mensaje no puede exceder el módulo. Altamente costoso en CPU, debe reservarse para encapsular llaves (KEM).")

    case 7:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            s_doc = st.text_area("Documento Legal", value="CONTRATO: ALICE AUTORIZA PAGO DE $1000")
            if st.button("Firmar Digitalmente", type="primary", use_container_width=True):
                t0 = time.perf_counter()
                b_firma = st.session_state.claves_rsa_alice.sign(s_doc.encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
                tf = time.perf_counter()
                st.session_state.canal_7 = {"doc": s_doc, "firma": b_firma}
                st.session_state.recursos_7 = {"tiempo": tf-t0, "memoria": sys.getsizeof(b_firma)}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante)</h4>", unsafe_allow_html=True)
            if "canal_7" in st.session_state:
                s_ataque = st.selectbox("Laboratorio de Eve", ["Observar", "Modificar un mensaje firmado"])
                d_mod = st.session_state.canal_7.copy()
                if s_ataque == "Modificar un mensaje firmado":
                    d_mod["doc"] = "CONTRATO: ALICE AUTORIZA PAGO DE $9000 A EVE"
                    st.error("Eve manipuló las condiciones del documento.")
                st.session_state.canal_7_mod = d_mod
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_7_mod" in st.session_state:
                d_rx = st.session_state.canal_7_mod
                try:
                    st.session_state.claves_rsa_alice.public_key().verify(d_rx["firma"], d_rx["doc"].encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
                    st.success("Bob valida que la firma es auténtica y proviene de Alice.")
                except InvalidSignature:
                    st.error("Aprendizaje: La firma deja de verificarse, previniendo falsificaciones.")
        st.divider()
        if "recursos_7" in st.session_state:
            renderizar_ficha("Documento, Llave Privada", "Criptografía RSA, Esquema PSS, Función Hash", "Proteger: Llave Privada. Público: Documento, Firma, Llave Pública", "Firma Digital en bytes", "No repudio, Autenticación de Origen e Integridad", st.session_state.recursos_7, "La llave privada debe resguardarse mediante enclaves o hardware criptográfico.")

    case 8:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            if st.button("Generar y Enviar Material ECDH", type="primary", use_container_width=True):
                t0 = time.perf_counter()
                o_priv_a = ec.generate_private_key(ec.SECP256R1())
                o_pub_a = o_priv_a.public_key()
                tf = time.perf_counter()
                st.session_state.canal_8_a = {"priv": o_priv_a, "pub": o_pub_a}
                st.session_state.recursos_8 = {"tiempo": tf-t0, "memoria": sys.getsizeof(o_pub_a)}
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_8_a" in st.session_state:
                if st.button("Generar Respuesta ECDH", type="primary", use_container_width=True):
                    o_priv_b = ec.generate_private_key(ec.SECP256R1())
                    o_pub_b = o_priv_b.public_key()
                    st.session_state.canal_8_b = {"priv": o_priv_b, "pub": o_pub_b}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante)</h4>", unsafe_allow_html=True)
            if "canal_8_a" in st.session_state and "canal_8_b" in st.session_state:
                s_ataque = st.selectbox("Laboratorio de Eve", ["Observar", "Sustituir Valores Públicos (MitM)"])
                if s_ataque == "Sustituir Valores Públicos (MitM)":
                    o_priv_eve = ec.generate_private_key(ec.SECP256R1())
                    o_pub_eve = o_priv_eve.public_key()
                    st.session_state.canal_8_pub_a = o_pub_eve
                    st.session_state.canal_8_pub_b = o_pub_eve
                    st.error("Eve secuestró el intercambio entregando su propia llave pública a ambos nodos.")
                else:
                    st.session_state.canal_8_pub_a = st.session_state.canal_8_a["pub"]
                    st.session_state.canal_8_pub_b = st.session_state.canal_8_b["pub"]

                if st.button("Cerrar Intercambio"):
                    b_shared_a = st.session_state.canal_8_a["priv"].exchange(ec.ECDH(), st.session_state.canal_8_pub_b)
                    b_shared_b = st.session_state.canal_8_b["priv"].exchange(ec.ECDH(), st.session_state.canal_8_pub_a)
                    st.session_state.final_8 = (b_shared_a, b_shared_b)
        if "final_8" in st.session_state:
            st.divider()
            if s_ataque == "Sustituir Valores Públicos (MitM)":
                st.error("Escenario de Filtración: Alice y Bob derivaron secretos diferentes y Eve posee control total bidireccional. Aprendizaje: Un acuerdo de claves necesita autenticar a los participantes para evitar ataques de Hombre-en-el-Medio.")
            else:
                st.success("Secreto acordado uniformemente sin visibilidad para observadores pasivos.")
            if "recursos_8" in st.session_state:
                renderizar_ficha("Materiales Elípticos Base", "Puntos de Curva Elíptica (SECP256R1)", "Proteger: Secretos Aleatorios Privados y la Llave Derivada final. Público: Puntos X,Y del generador", "Secreto Maestro Compartido", "Establecimiento Efímero de Claves", st.session_state.recursos_8, "Obligatorio aplicar firmas digitales o certificados sobre las llaves públicas para asegurar autenticidad de los extremos.")

    case 9:
        with col_alice:
            st.markdown("<h4 style='color: #333333;'>Alice (Emisor)</h4>", unsafe_allow_html=True)
            if st.button("Enviar Identidad (Certificado)", type="primary", use_container_width=True):
                s_identidad = b"ALICE_CORP_ROOT_CERT"
                t0 = time.perf_counter()
                b_firma_ca = st.session_state.ca_privada.sign(s_identidad, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
                tf = time.perf_counter()
                st.session_state.canal_9 = {"id": s_identidad, "firma": b_firma_ca}
                st.session_state.recursos_9 = {"tiempo": tf-t0, "memoria": sys.getsizeof(b_firma_ca)}
        with col_eve:
            st.markdown("<h4 style='color: #333333;'>Eve (Atacante)</h4>", unsafe_allow_html=True)
            if "canal_9" in st.session_state:
                s_ataque = st.selectbox("Laboratorio de Eve", ["Observar", "Presentar un certificado de una CA no confiable"])
                d_mod = st.session_state.canal_9.copy()
                if s_ataque == "Presentar un certificado de una CA no confiable":
                    d_mod["id"] = b"EVE_CORP_PHISHING_CERT"
                    d_mod["firma"] = st.session_state.ca_falsa.sign(d_mod["id"], padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
                    st.error("Eve sustituyó el bloque por un certificado firmado con su CA local.")
                st.session_state.canal_9_mod = d_mod
        with col_bob:
            st.markdown("<h4 style='color: #333333;'>Bob (Receptor)</h4>", unsafe_allow_html=True)
            if "canal_9_mod" in st.session_state:
                d_rx = st.session_state.canal_9_mod
                try:
                    st.session_state.ca_privada.public_key().verify(d_rx["firma"], d_rx["id"], padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
                    st.success(f"Certificado validado por la Autoridad Central: {d_rx['id'].decode()}")
                except InvalidSignature:
                    st.error("Aprendizaje: Bob rechaza la conexión al determinar que la cadena de confianza pertenece a una CA no confiable (Firma Root Inválida).")
        st.divider()
        if "recursos_9" in st.session_state:
            renderizar_ficha("Identidad de Entidad, Material Público", "Llaves asimétricas, Infraestructura X.509, Entidad Certificadora", "Proteger: Llave privada de la CA Raíz. Público: Certificado y Estructura Jerárquica", "Certificado Firmado", "Confianza, Identidad Federada", st.session_state.recursos_9, "La lista de revocación (CRL) y los certificados raíces del sistema receptor deben estar absolutamente actualizados y protegidos.")

    case 10:
        st.markdown("<h3 style='color: #cc0000;'>Reporte de Fiabilidad y Vulnerabilidades</h3>", unsafe_allow_html=True)
        st.markdown("A partir de las evaluaciones observadas mediante los laboratorios de intervención de Eve, se debate y determinan las siguientes pautas:")
        st.markdown("- **Cifrados Simétricos No Autenticados (AES-CBC, AES-CTR, ChaCha20):** Mostraron vulnerabilidad letal a la manipulación directa de bytes sin activar fallos. **No son confiables por sí solos.** Deben integrarse con códigos MAC en topología *Encrypt-then-MAC* o utilizar variantes GCM/Poly1305.")
        st.markdown("- **Funciones Hash Básicas (SHA-256):** Vulnerables contra diccionarios en contextos de autenticación de usuarios. **Se consideran poco confiables** para resguardo de credenciales; se imponen modelos KDF como Scrypt o Argon2.")
        st.markdown("- **Acuerdos de Claves (ECDH puro):** Eve demostró un secuestro MitM total. **No es confiable** sin una capa asimétrica adicional de Firmas Digitales basadas en un certificado raíz.")
        st.markdown("- **Ataques de Repetición (Replay):** Cualquier cifrado que opere de manera puramente funcional sin observar el estado de red fue engañado repitiendo el paquete. La validación requiere estricto rastreo de nonces y ventanas de tiempo (Timestamps).")
        
        st.markdown("<h4 style='color: #333333;'>Tabla Estructural de Primitivas Criptográficas</h4>", unsafe_allow_html=True)
        st.markdown('''
| Categoría | Mecanismo Base | Componentes Esenciales | Propiedad Resultante | Consecuencia de Mal Uso |
|---|---|---|---|---|
| Sin Llave | Hash Criptográfico | Función Matemática (SHA2, SHA3) | Integridad, Resistencia Colisión | Hashear sin sal permite tablas Rainbow y recuperación por diccionario. |
| Sin Llave | XOF (Esponja) | Fase de Absorción y Expresión | Extensibilidad Adaptable | Usar longitudes reducidas induce colisiones. |
| Simétrico | Bloques (AES-CTR) | Llave AES, Nonce, Contador | Confidencialidad | Reutilizar el Nonce o Contador destruye el cifrado por completo. |
| Simétrico | Flujo (ChaCha20) | Llave de Flujo, Nonce | Confidencialidad Continua | Maleabilidad total; el receptor no detectará alteraciones activas. |
| Simétrico | Autenticado (GCM) | Llave, IV, Datos Asociados, Etiqueta | Confidencialidad e Integridad | El reúso del IV filtra el polinomio de autenticación y compromete la llave H. |
| Simétrico | HMAC | Función Hash, Llave Simétrica | Integridad y Autenticidad | Usar llaves menores al bloque de la función Hash degrada la seguridad. |
| Simétrico | Derivación KDF | Sal Aleatoria, CPU/RAM Costos | Protección de Contraseñas | Parámetros computacionales débiles permiten la fuerza bruta asintótica. |
| Asimétrico| Encriptación Pública | Llave Pública, Privada, Relleno | Intercambio de Secretos | Prescindir del padding (OAEP) permite ataques algebraicos. |
| Asimétrico| Firma Digital RSA | Llave Pública, Privada, Relleno | No repudio e Identidad | Firmar un documento sin aplicar Hash previamente vulnera el esquema. |
| Asimétrico| PKI | Certificados X.509, CA Raíz | Confianza de Red Distribuida | CA comprometida provoca falsificación de cualquier entidad dependiente. |
        ''')