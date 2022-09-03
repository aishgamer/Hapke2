$(document).ready(function () {

// Hapke Step Start ------------------------------------------------------------------

$(".jschkbox").change(function() {
    var chkid = $(this).attr('id');
    var elt_prefix = chkid.replace('toggle','');

    //Single Scattering Albedo - Inversion
    if(chkid=='w_inversion'){
        if(this.checked) {
            $('#hpk_w_toggle').prop("checked", false);
            $('#hpk_w_guess').prop( "disabled", true);
            $('#hpk_w_low').prop( "disabled", true);
            $('#hpk_w_high').prop( "disabled", true);
        }
        else{
            $('#hpk_w_toggle').prop("checked", true);
            $('#hpk_w_guess').prop( "disabled", false);
            $('#hpk_w_low').prop( "disabled", false);
            $('#hpk_w_high').prop( "disabled", false);
        }
        return;
    }

    //Generic
    if(this.checked) {
        if(chkid=='hpk_w_toggle'){
            $('#w_inversion').prop("checked", false);
        }
        // Enable elements
        $('#'+elt_prefix+'guess').prop( "disabled", false);
        $('#'+elt_prefix+'low').prop( "disabled", false);
        $('#'+elt_prefix+'high').prop( "disabled", false);
    }
    else{
        if(chkid=='hpk_w_toggle'){
            $('#w_inversion').prop("checked", true);
        }
        // Disable Elements
        $('#'+elt_prefix+'guess').prop( "disabled", true);
        $('#'+elt_prefix+'low').prop( "disabled", true);
        $('#'+elt_prefix+'high').prop( "disabled", true);
    }
});

// Hapke Step End ------------------------------------------------------------------
});