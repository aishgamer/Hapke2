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
                $('#input_results_sciplot').empty().append(data.img);
                $('#wstable').bootstrapTable('load', data.wsdata).show();

                $('#dqtable').bootstrapTable('removeAll');
                $('#dqtable').bootstrapTable('load', data.dq_results).show();

                // For next section - setting defaults
                $('#minValdp').text(data.min_wave);
                $('#maxValdp').text(data.max_wave);
                $('#pp_crop_min_input').attr({ 'min': data.min_wave, 'max': data.max_wave - 100 })
                $('#pp_crop_max_input').attr({ 'min': data.min_wave + 100, 'max': data.max_wave })
                var msg = 
                'Data Quality - All:'+ data.dq_str + '.'
                $('#input_message').html(msg);
                
                //Plotly Data
                var json_plt_data = [{
                    opacity:0.5,
                    type: 'scatter3d',
                    x: data.plot_data.wave,
                    y: data.plot_data.g,
                    z: data.plot_data.refl,
                    mode: 'markers',
                    marker: {
                        color: 'rgb(127, 127, 127)',
                        size: 3,
                        symbol: 'circle',
                        line: {
                        color: 'rgb(204, 204, 204)',
                        width: 1},
                        opacity: 0.8}
                }];
                
                var layout = {title: "Input Data",
                scene: {
                    xaxis:{title: 'Wavelength'},
                    yaxis:{title: 'Phase Angle'},
                    zaxis:{title: 'Reflectance'}
                    },
                margin: {l: 0, r: 0, b: 0,t: 0}                
                };
                Plotly.newPlot("input_results", json_plt_data, layout);
            },
        });

    });

    $('.fnshowbtn').click(function(){
        $('.fnsection').hide();
        var sec_id = $(this).attr('d-id');
        $('#'+sec_id).show();
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
                $('#pp_results').empty().append(data.img);
                $('#wstable').bootstrapTable('removeAll');
                $('#wstable').bootstrapTable('load', data.wsdata).show();
                
                $('#pp_dqtable').bootstrapTable('removeAll');
                $('#pp_dqtable').bootstrapTable('load', data.dq_results).show();

                var msg = 
                'Data Quality - All:'+ data.dq_str + '.'
                $('#pp_message').html(msg);

                // For next section - enabling disabling fields
                if(data.guess_permission == 'red'){
                    $('.lh_guess').prop('disabled', true);
                }
                else{
                    $('.lh_guess').prop('disabled', false);
                }
            },
        });
    });
});