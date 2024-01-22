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

$("form[name=form_editar_usuario]").submit(function(e){
    var $form = $(this);
    var $alert = $form.find(".alert");
    var data = $form.serialize();

    $.ajax({
        url: "/editar_administrador",
        type: "POST",
        data: data,
        dataType: "json",
        success:function (resp) {
            console.log("SUCCESS: ", resp.success)
            $('#alertaTitulo').text('Listo!! ');
            $('#alertaCuerpo').text(resp.success);
            $alert.addClass("alert-success").removeClass("visually-hidden");
            window.location.href = '/admin/editar_usuario'
        },
        error: function(resp) {
            console.log("ERROR: ", resp);
            $('#alertaTitulo').text('Error ');
            $('#alertaCuerpo').text(resp.responseJSON.error);
            $alert.addClass("alert-danger").removeClass("visually-hidden");
        }

    });

    e.preventDefault();
})

