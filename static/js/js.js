$(document).ready(function(){

    $('#login').click(function(){
        $('.login-form').addClass('popup');
    });

    $('.login-form form .fa-times').click(function(){
        $('.login-form').removeClass('popup');
    });

    $('#signup').click(function(){
        $('.signup-form').addClass('popup');
    });

    $('.signup-form form .fa-times').click(function(){
        $('.signup-form').removeClass('popup');
    });

    $('#adsignup').click(function(){
        $('.adsignup-form').addClass('popup');
    });

    $('.adsignup-form form .fa-times').click(function(){
        $('.adsignup-form').removeClass('popup');
    });

    $('#admin').click(function(){
        $('.admin-login-form').addClass('popup');
    });

    $('.admin-login-form form .fa-times').click(function(){
        $('.admin-login-form').removeClass('popup');
    });

});

// singup
$("form[name=signup_form]").submit(function(e){
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
    
    $.ajax({
        url: "/user/signup",
        type: "POST",
        data: data,
        dataType: "json",
        success: function(resp){
            window.location.href = "/dashboard/";
        },
        error: function(resp){
            $error.text(resp.responseJSON.error).removeClass("error--hidden");

        }
    });
    e.preventDefault();
})

// admin signup

$("form[name=adsignup_form]").submit(function(e){
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
    
    $.ajax({
        url: "/user/adsignup",
        type: "POST",
        data: data,
        dataType: "json",
        success: function(resp){
            window.location.href = "/adashboard/";
        },
        error: function(resp){
            $error.text(resp.responseJSON.error).removeClass("error--hidden");

        }
    });
    e.preventDefault();
})


// login
$("form[name=login_form]").submit(function(e){
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
    
    $.ajax({
        url: "/user/login",
        type: "POST",
        data: data,
        dataType: "json",
        success: function(resp){
            window.location.href = "/dashboard/";
        },
        error: function(resp){
            $error.text(resp.responseJSON.error).removeClass("error--hidden");

        }
    });
    e.preventDefault();
})

// admin login
$("form[name=admin_login_form]").submit(function(e){
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
    
    $.ajax({
        url: "/user/admin",
        type: "POST",
        data: data,
        dataType: "json",
        success: function(resp){
            window.location.href = "/adashboard/";
        },
        error: function(resp){
            $error.text(resp.responseJSON.error).removeClass("error--hidden");

        }
    });
    e.preventDefault();
})