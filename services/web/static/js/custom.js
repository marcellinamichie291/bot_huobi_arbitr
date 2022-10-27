(function ($) {

    "use strict";

    let selected = [];

    $('#pairs_list_raw').change(function() {
        // var selected_list = $(this).val().join();

        const values = $(this).val();
        // Remove all non selected from selected array if user has deselected something
        selected = selected.filter((value) => values.includes(value));
        // get value which is not in selected list
        const lastSelected = values.filter((value) => !selected.includes(value));
        // push to selected array
        selected.push(lastSelected[0]);

        var input = $('.admin-form').find('input[name="pairs_order"]')
        if (input.length === 0){
            $('.admin-form').append($(`<input name="pairs_order" type="hidden" value="${selected.join()}">`));
        } else {
            input.attr('value', selected.join());
        }
    });

}(jQuery));
