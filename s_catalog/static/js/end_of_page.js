var current_ads_idx = 0;
var ADS_UPDATE_STEP = 10;

function populate_sub_categories_in_search_bar() {
    //populate sub-categories in search bar according to category selected by user 
    //called on change in category
    var selected_category = $("#category-selected option:selected").text();
    console.log(selected_category);

    var selected_sub_category_id = $("#sub-category-selected");

    var list_of_selected_sub_categories = all_categories[selected_category].value;
    console.log(list_of_selected_sub_categories);

    //reset menu if there was some category selected before and show user that 
    //they can now select a sub-category
    selected_sub_category_id.find("option").remove().end();
    selected_sub_category_id.append($("<option selected disabled/>").val("Select Sub - Category").text("Select Sub - Category"));
    $.each(list_of_selected_sub_categories, function(index, value) {
        selected_sub_category_id.append($("<option />").val(value.id).text(value.name));
    });
}

function build_filters() {

    var selected_city = $("#search-city-select").val();
    var selected_category_id = $("#category-selected").val();
    var selected_sub_category_id = $("#sub-category-selected").val();
    var select_ads_within_days = $("#select-ads-within-days").val();
    var min_idx = current_ads_idx;

    var filters = {
        "selected_city": selected_city,
        "selected_category_id": selected_category_id,
        "selected_sub_category_id": selected_sub_category_id,
        "select_ads_within_days": select_ads_within_days,
        "min_idx": min_idx
    };

    return filters;
}

function reset_ads_counter() {
    current_ads_idx = 0;
}

function increment_ads_counter() {
    current_ads_idx = current_ads_idx + ADS_UPDATE_STEP;
}

function decrement_ads_counter() {
    current_ads_idx = current_ads_idx - ADS_UPDATE_STEP;
    if (current_ads_idx<0){
        current_ads_idx = 0;
    }
}

function search_button() {
    reset_ads_counter();
    filters = build_filters();
    update_ads(filters);
}


function render_ads_list(ads) {
    var selected_ads_id = $("#displayed_ads");
    selected_ads_id.html("");
 
    $.each(ads, function(index, value) {
        selected_ads_id.append(value);
    });

}


function update_ads(request) {
    var request_url = "/update_ads_list";

    $.ajax({
        dataType: "json",
        url: request_url,
        data: request,
        success: render_ads_list
    });


}

function update_ads_list(counter_update_function){
    counter_update_function();
    filters = build_filters();
    update_ads(filters);
}

function load_initial_list_of_ads(){
    //called on initialization, shows all ads in database by 10 sorted by date 
    //
    console.log("load_inital_list_of_ads");
    update_ads_list(increment_ads_counter);

}

function show_next_ads(){
    update_ads_list(increment_ads_counter);
}

function show_prev_ads(){
    update_ads_list(decrement_ads_counter);
}

$("#next_button").click(show_next_ads);
$("#prev_button").click(show_prev_ads);
$("#search-button").click(search_button);
$(document).ready(load_initial_list_of_ads);
