$("form[name=form_iniciar_sesion]").submit(function(e){
    var $form = $(this);
    var $error = $form.find(".alert");
    var data = $form.serialize();

    $.ajax({
        url: "/iniciar_sesion_usuario",
        type: "POST",
        data: data,
        dataType: "json",
        success:function (resp) {
            window.location.href = '/'
        },
        error: function(resp) {
            console.log(resp);
            $error.removeClass("visually-hidden");
        }

    });

    e.preventDefault();
})