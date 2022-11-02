'''
Este archivo contiene las constantes utilizadas por los archivos "modulo_suministros.py";
"modulo_producciones.py"
'''

DESTINO_INT_CC_SIGCOM = {
    "ANATOMIA PATOLOGICA": "544-ANATOMÍA PATOLÓGICA",
    "BODEGA ALIMENTACION": "652-SERVICIO DE ALIMENTACIÓN",
    "BODEGA CENTRAL ABASTECIMIENTO": "670-ADMINISTRACIÓN",
    "BODEGA DE CONSULTORIO EXTERNO": "670-ADMINISTRACIÓN",
    "BODEGA DE KINESITERAPIA": "15010-CONSULTA OTROS PROFESIONALES",
    "BODEGA ECOCARDIO": "537-ECOCARDIOGRAFÍA",
    "BODEGA ELECTROFISIOLOGIA": "15026-PROCEDIMIENTOS DE CARDIOLOGÍA",
    "BODEGA COMUNICACIONES Y RELACIONES PUBLICAS": "670-ADMINISTRACIÓN",
    "BODEGA HEMODINAMIA": "253-PROCEDIMIENTOS DE HEMODINAMIA",
    "BODEGA INTERMEDIO": "66-HOSPITALIZACIÓN MEDICINA INTERNA",
    "BODEGA INTERMEDIO INDIFERENCIADO 3 5° Piso Norte": "66-HOSPITALIZACIÓN MEDICINA INTERNA",
    "BODEGA INTERMEDIO MEDICINA 3° NORTE": "66-HOSPITALIZACIÓN MEDICINA INTERNA",
    "BODEGA INTERMEDIO–UCI 4° SUR": "66-HOSPITALIZACIÓN MEDICINA INTERNA",
    "BODEGA PERECIBLES": "652-SERVICIO DE ALIMENTACIÓN",
    "BODEGA TRANSPLANTE CARDIO-PULMONAR": "484-QUIRÓFANOS TORACICA",
    "BODEGA UCI": "166-UNIDAD DE CUIDADOS INTENSIVOS",
    "BRONCOSCOPIA": "267-PROCEDIMIENTOS ENDOSCÓPICOS",
    "ESTERILIZACION": "95301-CENTRAL DE ESTERILIZACIÓN",
    "ESTUDIO DEL SUEÑO": "15010-CONSULTA OTROS PROFESIONALES",
    "IMAGENOLOGIA": "41108-IMAGENOLOGÍA",
    "INFORMATICA": "670-ADMINISTRACIÓN",
    "LAB. ANAT. PATOLOGICA": "544-ANATOMÍA PATOLÓGICA",
    "LAB. FISIOPATOLOGIA": "518-LABORATORIO CLÍNICO",
    "LAB. HEMATOLOGIA": "518-LABORATORIO CLÍNICO",
    "LAB. INMUNOLOGIA": "518-LABORATORIO CLÍNICO",
    "LAB. MICROBIOLOGIA": "518-LABORATORIO CLÍNICO",
    "LAB. QUIMICA": "518-LABORATORIO CLÍNICO",
    "LAB. TOMA DE MUESTRA": "518-LABORATORIO CLÍNICO",
    "LAB. TUBERCULOSIS": "518-LABORATORIO CLÍNICO",
    "LAB. UMT (UND.MED.TRANSFUSIONAL": "518-LABORATORIO CLÍNICO",
    "LABORATORIO CLINICO": "518-LABORATORIO CLÍNICO",
    "NEUMOLOGIA BODEGA CENTRAL": "267-PROCEDIMIENTOS ENDOSCÓPICOS",
    "PABCRT": "PABELLÓN",
    "PABELLÓN": "PABELLÓN",
    "PABPYX": "PABELLÓN",
    "RECETARIO HOSPITALIZADO": "670-ADMINISTRACIÓN",
    "SALA SMQCV": "464-QUIRÓFANOS CARDIOVASCULAR",
    "SECRE UCI": "166-UNIDAD DE CUIDADOS INTENSIVOS",
    "SECRE. ADMISION": "670-ADMINISTRACIÓN",
    "SECRE. ANALISIS CLINICO": "518-LABORATORIO CLÍNICO",
    "SECRE. CARDIOCIRUGIA": "464-QUIRÓFANOS CARDIOVASCULAR",
    "SECRE. CONGENITO": "670-ADMINISTRACIÓN",
    "SECRE. COORDINADORA GES": "670-ADMINISTRACIÓN",
    "SECRE. DIRECCION": "670-ADMINISTRACIÓN",
    "SECRE. FARMACIA": "670-ADMINISTRACIÓN",
    "SECRE. LOGISTICA": "670-ADMINISTRACIÓN",
    "SECRE. NEUMOLOGIA": "15022-PROCEDIMIENTO DE NEUMOLOGÍA",
    "SECRE. NUTRICION": "652-SERVICIO DE ALIMENTACIÓN",
    "SECRE. RECURSOS HUMANOS": "670-ADMINISTRACIÓN",
    "SECRE. SERVICIO SOCIAL": "670-ADMINISTRACIÓN",
    "SECRE. SUBDIR. DE ENFERMERIA": "670-ADMINISTRACIÓN",
    "SECRE. UNIDAD DE COMPRA": "670-ADMINISTRACIÓN",
    "UNIDAD DE IAAS": "670-ADMINISTRACIÓN",
    "UNIDAD DOCENTE ASISTENCIA": "670-ADMINISTRACIÓN",
    "FARMACIA HOSPITALIZADO": "30-MEDICAMENTOS",
    "FARMACIA POLICLINICO": "30-MEDICAMENTOS",
    "SECRE. CIRUGIA DE TORAX": "484-QUIRÓFANOS TORACICA",
    "LAB. DE URGENCIA": "518-LABORATORIO CLÍNICO",
    "SECRE. CONTABILIDAD": "670-ADMINISTRACIÓN",
    "UNIDAD DE ONCOLOGIA": "260-PROCEDIMIENTO ONCOLOGÍA",
    "BODEGA UCI 5° Piso Norte": "166-UNIDAD DE CUIDADOS INTENSIVOS",
    "SECRE. GESTION DE CAMA": "66-HOSPITALIZACIÓN MEDICINA INTERNA",
    "UNIDAD DE CALIDAD": "670-ADMINISTRACIÓN",
    "POLI ALIVIO DEL DOLOR": "15010-CONSULTA OTROS PROFESIONALES",
    "UNIDAD DE LICITACIONES Y CONTRATOS": "670-ADMINISTRACIÓN",
    "No definido": None,
    "INT": None,
    "Hospital del Salvador": None,
    "Externo": None,
    "Instituto Nacional de Geriatría": None
}

TRADUCTOR_ITEM_SIGFE_ITEM_SIGCOM_JSON = {
    "Equipos menores": "8-EQUIPOS MENORES",
    "Insumos, repuestos y accesorios computacionales": "27-MATERIALES INFORMATICOS",
    "Mantenimiento y Reparacion de Maquinas y Equipos de Oficina":
    "28-MATERIALES PARA MANTENIMIENTO Y REPARACIONES DE INMUEBLES",
    "Mantenimiento y Reparación de Otras Maquinarias y Equipos Correctivos":
    "44-REPUESTOS Y ACCESORIOS PARA MANTENIMIENTO Y REPARACIONES DE VEHICULOS",
    "Material de Laboratorio": "18-MATERIAL MEDICO QUIRURGICO",
    "Materiales de oficina": "24-MATERIALES DE OFICINA, PRODUCTOS DE PAPEL E IMPRESOS",
    "Materiales y útiles quirúrgicos": "18-MATERIAL MEDICO QUIRURGICO",
    "Menaje para oficina, casino y otros": "31-MENAJE PARA OFICINA, CASINO Y OTROS",
    "Otros Insumos clínicos": "18-MATERIAL MEDICO QUIRURGICO",
    "Otros materiales y útiles de aseo": "29-MATERIALES Y ELEMENTOS DE ASEO",
    "Otros materiales, repuestos y útiles diversos para mantenimiento y reparaciones":
    "44-REPUESTOS Y ACCESORIOS PARA MANTENIMIENTO Y REPARACIONES DE VEHICULOS",
    "Otros químicos": "41-PRODUCTOS QUÍMICOS",
    "Otros textiles act hospitalaria": "43-PRODUCTOS TEXTILES, VESTUARIO Y CALZADO",
    "Oxigeno y gases clínicos": "9-GASES MEDICINALES", "Para personas-Pacientes": "46-VÍVERES",
    "Prótesis": "16-MATERIAL DE OSTEOSÍNTESIS Y PRÓTESIS",
    "Otros Insumos clínicos - Compras Intermediadas": "18-MATERIAL MEDICO QUIRURGICO"}

DICCIONARIO_UNIDADES_A_DESGLOSAR = {
    "41108-IMAGENOLOGÍA": [
        "41107-TOMOGRAFÍA",
        "41108-IMAGENOLOGÍA"
    ],
    "PABELLÓN": [
        "464-QUIRÓFANOS CARDIOVASCULAR",
        "484-QUIRÓFANOS TORACICA"
    ],
    "518-LABORATORIO CLÍNICO": [
        "51001-BANCO DE SANGRE",
        "518-LABORATORIO CLÍNICO"
    ],
    "66-HOSPITALIZACIÓN MEDICINA INTERNA": [
        "90-HOSPITALIZACIÓN QUIRÚRGICA",
        "66-HOSPITALIZACIÓN MEDICINA INTERNA"
    ],
    "253-PROCEDIMIENTOS DE HEMODINAMIA": [
        "270-PROCEDIMIENTOS TAVI",
        "264-PROCEDIMIENTOS EBUS",
        "15022-PROCEDIMIENTO DE NEUMOLOGÍA",
        "253-PROCEDIMIENTOS DE HEMODINAMIA"
    ],
    "15026-PROCEDIMIENTOS DE CARDIOLOGÍA": [
        "265-PROCEDIMIENTOS ECMO",
        "15105-CONSULTA CARDIOLOGÍA",
        "15220-CONSULTA CIRUGIA CARDIACA",
        "15201-CONSULTA CIRUGÍA GENERAL",
        "15026-PROCEDIMIENTOS DE CARDIOLOGÍA"
    ],
    "166-UNIDAD DE CUIDADOS INTENSIVOS": [
        "195-UNIDAD DE TRATAMIENTO INTENSIVO ADULTO",
        "166-UNIDAD DE CUIDADOS INTENSIVOS"
    ],
    "15038-PROCEDIMIENTO ONCOLOGÍA": [
        "15123-PROGRAMA MANEJO DEL DOLOR",
        "15107-CONSULTA ONCOLOGÍA",
        "15038-PROCEDIMIENTO ONCOLOGÍA"
    ],
    "670-ADMINISTRACIÓN": [
        "15008-CONSULTA NUTRICIÓN"
    ],
    "CONSULTAS CON MANEJO DEL DOLOR": [
        "15220-CONSULTA CIRUGIA CARDIACA",
        "15201-CONSULTA CIRUGÍA GENERAL",
        "15010-CONSULTA OTROS PROFESIONALES",
        "15111-CONSULTA NEUMOLOGÍA",
        "15107-CONSULTA ONCOLOGÍA",
        "15105-CONSULTA CARDIOLOGÍA",
        "15008-CONSULTA NUTRICIÓN",
        "15123-PROGRAMA MANEJO DEL DOLOR"
    ],
    "CONSULTAS SIN MANEJO DEL DOLOR": [
        "15220-CONSULTA CIRUGIA CARDIACA",
        "15201-CONSULTA CIRUGÍA GENERAL",
        "15010-CONSULTA OTROS PROFESIONALES",
        "15111-CONSULTA NEUMOLOGÍA",
        "15107-CONSULTA ONCOLOGÍA",
        "15105-CONSULTA CARDIOLOGÍA",
        "15008-CONSULTA NUTRICIÓN"
    ]
}

UNIDADES_PROPORCIONALES_A_LA_PRODUCCION = ["41108-IMAGENOLOGÍA", "PABELLÓN",
                                           "518-LABORATORIO CLÍNICO",
                                           "66-HOSPITALIZACIÓN MEDICINA INTERNA",
                                           "166-UNIDAD DE CUIDADOS INTENSIVOS",
                                           "CONSULTAS CON MANEJO DEL DOLOR",
                                           "CONSULTAS SIN MANEJO DEL DOLOR"]

VALOR_TAVI_SUMINISTROS = 22784797
VALOR_EBUS_SUMINISTROS = 4408972
VALOR_ECMO_SUMINISTROS = 3092453
PORCENTAJES_A_CONSULTAS_CARDIOLOGIA = 0.15
PORCENTAJES_A_PROCEDIMIENTOS_CARDIOLOGIA = 0.85

PORCENTAJES_A_CONSULTAS_ONCOLOGIA = 0.15
PORCENTAJES_A_PROCEDIMIENTOS_ONCOLOGIA = 0.85

VALOR_CONSULTAS_ADMIN_SUMINISTROS = 5314

WINSIG_ERVICIO_FARMACIA_CC_SIGCOM = {
    "HMQ RESPIRATORIO SALA": "66-HOSPITALIZACIÓN MEDICINA INTERNA",
    "INTERMEDIO INDIFERENCIADO 1 [4°Piso Sector Norte] cardio":
    "195-UNIDAD DE TRATAMIENTO INTENSIVO ADULTO",
    "INTERMEDIO INDIFERENCIADO 2 [4°Piso Sector Sur] resp":
    "195-UNIDAD DE TRATAMIENTO INTENSIVO ADULTO",
    "INTERMEDIO INDIFERENCIADO 3 [5°Piso Sector Norte]":
    "195-UNIDAD DE TRATAMIENTO INTENSIVO ADULTO",
    "MÉDICO QUIRURGICO CARDIOVASCULAR[4°Piso Sector Norte]": "102-HOSPITALIZACIÓN CARDIOVASCULAR",
    "QUIMIOTERAPIA INT [3 Piso Sur]": None,
    "ELECTROFISIOLOGÍA": "253-PROCEDIMIENTOS DE HEMODINAMIA",
    "HEMODINAMIA": "253-PROCEDIMIENTOS DE HEMODINAMIA",
    "BRONCOSCOSPIA": "267-PROCEDIMIENTOS ENDOSCÓPICOS", "UCI": "166-UNIDAD DE CUIDADOS INTENSIVOS",
    "UCI-UTI2": "166-UNIDAD DE CUIDADOS INTENSIVOS",
    "UCI-UTI3": "166-UNIDAD DE CUIDADOS INTENSIVOS",
    "UTI-401": "195-UNIDAD DE TRATAMIENTO INTENSIVO ADULTO",
    "UTI-MEDICINA": "195-UNIDAD DE TRATAMIENTO INTENSIVO ADULTO",
    "CAMAS MEDIAS respiratorio + cardiovascular": "66-HOSPITALIZACIÓN MEDICINA INTERNA",
    "B. PABELLON": None, "POLICLÍNICO": None,
    "POLICLÍNICO P. ALIVIO DEL DOLOR": "15123-PROGRAMA MANEJO DEL DOLOR"}
