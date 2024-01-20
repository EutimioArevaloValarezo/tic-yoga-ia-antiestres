var data = {
    "facultades": [
        {
            "nombre": "Facultad Agropecuaria y de Recursos Naturales Renovables",
            "acronimo": "FARNR",
            "carreras": [
                "Agronomía",
                "Ingeniería Agrícola",
                "Ingeniería Ambiental",
                "Ingeniería Forestal",
                "Medicina Veterinaria"
            ]
        },
        {
            "nombre": "Facultad de la Educación el Arte y la Comunicación",
            "acronimo": "FEAC",
            "carreras": [
                "Artes Visuales",
                "Pedagogía de la Lengua y la Literatura",
                "Comunicación",
                "Educación Básica",
                "Educación Especial",
                "Educación Inicial",
                "Pedagogía de la Actividad Física y Deporte",
                "Pedagogía de las Ciencias Experimentales - Informática",
                "Pedagogía de las Ciencias Experimentales - Matemáticas y la Física",
                "Pedagogía de las Ciencias Experimentales - Química y Biología",
                "Pedagogía de los Idiomas Nacionales y Extranjeros",
                "Artes Musicales",
                "Psicopedagogía"
            ]
        },
        {
            "nombre": "Facultad de la Energía, las Industrias y los Recursos Naturales no Renovables",
            "acronimo": "FEIRNNR",
            "carreras": [
                "Computación",
                "Electricidad",
                "Electromecánica",
                "Ingeniería Automotriz",
                "Minas",
                "Telecomunicaciones"
            ]
        },
        {
            "nombre": "Facultad Jurídica, Social y Administrativa",
            "acronimo": "FJSA",
            "carreras": [
                "Administración de Empresas",
                "Administración Pública",
                "Contabilidad y Auditoría",
                "Derecho",
                "Economía",
                "Finanzas",
                "Trabajo Social",
                "Turismo"
            ]
        },
        {
            "nombre": "Facultad Jurídica, Social y Administrativa",
            "acronimo": "FJSA",
            "carreras": [
                "Enfermería",
                "Laboratorio Clínico",
                "Medicina",
                "Odontología",
                "Psicología Clínica"
            ]
        },
        {
            "nombre": "Unidad de Educación a Distancia y en Línea",
            "acronimo": "UED",
            "carreras": [
                "Pedagogía de las Ciencias Experimentales - Informática (Modalidad en Línea)",
                "Educación Básica (Modalidad en Línea)",
                "Administración de Empresas (Modalidad a Distancia)",
                "Agronegocios (Modalidad a Distancia)",
                "Comunicación (Modalidad a Distancia)",
                "Contabilidad y Auditoría (Modalidad a Distancia)",
                "Derecho (Modalidad a Distancia)",
                "Psicopedagogía (Modalidad a Distancia)",
                "Trabajo Social (Modalidad a Distancia)",
                "Educación Inicial (Modalidad a Distancia)"
            ]
        }
    ]
}

// Cargar las facultades al cargar la página
window.onload = function () {
    var selectFacultad = document.getElementById("inputFacultad");
    for (var i = 0; i < data.facultades.length; i++) {
        var opt = document.createElement('option');
        opt.value = data.facultades[i].nombre;
        opt.innerHTML = data.facultades[i].nombre;
        selectFacultad.appendChild(opt);
    }
    cargarCarreras(0); // Cargar las carreras de la primera facultad
}

// Función para cargar las carreras cuando se selecciona una facultad
function cargarCarreras(indexFacultad) {
    var selectCarrera = document.getElementById("inputCarrera");
    selectCarrera.innerHTML = ""; // Limpiar las carreras anteriores
    for (var i = 0; i < data.facultades[indexFacultad].carreras.length; i++) {
        var opt = document.createElement('option');
        opt.value = data.facultades[indexFacultad].carreras[i];
        opt.innerHTML = data.facultades[indexFacultad].carreras[i];
        selectCarrera.appendChild(opt);
    }
}

$(document).ready(function () {
    $("#inputFacultad").change(function() {
        cargarCarreras(this.value);
    });
});

