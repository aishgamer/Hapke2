$(document).ready(function () { 
    //$("#input_submit").click(function () {
    //    $.ajax({
    //        type: 'GET',
    //        url: "/input_session",
    //        success: function (data) {
    //            $('#input_results').empty().append(data);
    //        }
    //    });
    //});

    $("#input_submit").click(function () {
        var formData = new FormData();
        formData.append('file', $('#input_file')[0].files[0]);
        $.ajax({
            type: 'POST',
            url: '/input_upload',
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                $('#wstable').bootstrapTable('removeAll');
                $('#input_results').empty().append(data.img);
                $('#wstable').bootstrapTable('load', data.wsdata).show();

                $('#dqtable').bootstrapTable('removeAll');
                $('#dqtable').bootstrapTable('load', data.dq_results).show();

                // For next section - setting defaults
                $('#minValdp').text(data.min_wave);
                $('#maxValdp').text(data.max_wave)
                $('#pp_crop_min_input').attr({ 'min': data.min_wave, 'max': data.max_wave - 100 })
                $('#pp_crop_max_input').attr({ 'min': data.min_wave + 100, 'max': data.max_wave })
                var msg = 
                'Data Quality - All:'+ data.dq_str + '.'
                $('#input_message').html(msg).wrap('<pre />');
            },
        });
    });

    $("#pp_submit").click(function () {
        var formData = new FormData(document.getElementById("pp_form"));
        console.log(formData)
        $.ajax({
            type: 'POST',
            url: '/input_preprocess',
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                console.log('Success!');
                console.log(data);
                $('#input_results').empty().append(data.img);
                $('#wstable').bootstrapTable('removeAll');
                $('#wstable').bootstrapTable('load', data.wsdata).show();
            },
        });
    });
});