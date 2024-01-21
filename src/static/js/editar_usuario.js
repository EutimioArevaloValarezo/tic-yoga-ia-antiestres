$(document).ready(function () {
    function togglePassword(input) {
        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
        } else {
            input.attr('type', 'password');
        }
    }

    $('#btn_pass_actual').click(function () {
        togglePassword($('#input_pass_actual'));
    });

    $('#btn_pass_nueva').click(function () {
        togglePassword($('#input_pass_nueva'));
    });

    $(document).ready(function () {
        // Agrega un evento de cambio al interruptor
        $('#swtich_contrasenia').change(function () {
            // Selecciona todos los campos de contraseña dentro del div-contenedor
            var passwordInputs = $('#div-contenedor input[type="password"]');

            // Verifica si el interruptor está activado
            if ($(this).is(':checked')) {
                // Si está activado, quita la clase visually-hidden del div-contenedor
                $('#div-contenedor').removeClass('visually-hidden');
                // Limpia los campos de contraseña
                passwordInputs.val('');
            } else {
                // Si está desactivado, agrega la clase visually-hidden al div-contenedor
                $('#div-contenedor').addClass('visually-hidden');
                // Limpia los campos de contraseña
                passwordInputs.val('');
            }
        });
    });
});

