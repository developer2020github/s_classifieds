var requested_ads_min_idx = 0;
var ADS_UPDATE_STEP = 10;
var total_number_of_ads_in_database = -1;

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

    var selected_city_id = $("#search-city-select").val();
    var selected_category_id = $("#category-selected").val();
    var selected_sub_category_id = $("#sub-category-selected").val();
    var select_ads_within_days = $("#select-ads-within-days").val();

    var requested_sort_by = $("#arrange-results-by").val();
    var sort_by = "";
    if (requested_sort_by !== "-1") {
        sort_by = requested_sort_by;
    }

    var min_idx = requested_ads_min_idx;

    var filters = {
        "selected_city_id": selected_city_id,
        "selected_category_id": selected_category_id,
        "selected_sub_category_id": selected_sub_category_id,
        "select_ads_within_days": select_ads_within_days,
        "min_idx": min_idx,
        "sort_by": sort_by
    };

    return filters;
}

function reset_ads_counter() {
    requested_ads_min_idx = 0;
}

function increment_ads_counter() {
    requested_ads_min_idx = requested_ads_min_idx + ADS_UPDATE_STEP;
    if (total_number_of_ads_in_database > -1) {
        //limit request to max theoretically possible number.
        //no need to set limit as per result of currently active filters - 
        //number displayed will be what database returns. 
        requested_ads_min_idx = Math.min(requested_ads_min_idx, total_number_of_ads_in_database);
    }
}

function decrement_ads_counter() {
    requested_ads_min_idx = Math.max(requested_ads_min_idx - ADS_UPDATE_STEP, 0);
}


function search_button() {
    reset_ads_counter();
    filters = build_filters();
    update_ads(filters);
}


function render_ads_list(ads) {
    var selected_ads_id = $("#displayed_ads");
    selected_ads_id.html("");

    $.each(ads.ads_html, function(index, value) {
        selected_ads_id.append(value);
    });

    var ads_sts = "";
    if (ads.total_number_of_ads > 0) {
        ads_sts = "Total of " + ads.total_number_of_ads + " ads selected.";
        ads_sts += "Displaying ads from " + ads.min_ad_idx_displayed + " to " + ads.max_ad_idx_displayed;
    } else {
        ads_sts = "No ads meet your search criteria"
    }

    $("#total-ads-selected").text(ads_sts);

    requested_ads_min_idx = parseInt(ads.min_ad_idx_displayed);

    //if total number of ads available is not set yet - this is initialization step, so set it
    if (total_number_of_ads_in_database === -1) {
        total_number_of_ads_in_database = parseInt(ads.total_number_of_ads)
    }

    update_selected_ads_info();
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


function update_ads_list(counter_update_function) {
    if (counter_update_function !== undefined) {
        counter_update_function();
    }

    filters = build_filters();
    update_ads(filters);

}


function load_initial_list_of_ads() {
    //called on initialization, shows all ads in database by 10 sorted by date 
    //
    console.log("load_inital_list_of_ads");
    $("#total-ads-selected").text(" Total of 0 ads selected");
    update_ads_list();
    update_selected_ads_info();
}


function show_next_ads() {
    update_ads_list(increment_ads_counter);
}


function show_prev_ads() {
    update_ads_list(decrement_ads_counter);
}


function get_item_info_for_display(item_name, default_text, item_id, default_value) {

    if ($(item_id).val() === default_value) {
        return default_text;
    }

    return (item_name + " : " + $(item_id + " option:selected").text());
}


function update_selected_ads_info() {

    $("#displayed-selected-city").text(get_item_info_for_display("Location", "Location : all", "#search-city-select", "-1"));
    $("#displayed-selected-category").text(get_item_info_for_display("Category", "Category : all", "#category-selected", "-1"));
    $("#displayed-selected-subcategory").text(get_item_info_for_display("Sub-Category", "Sub-Category : all", "#sub-category-selected", "-1"));
    $("#displayed-ads-posted-time").text(get_item_info_for_display("Ads posted", "Ads posted : any time", "#select-ads-within-days", "-1"));
    $("#displayed-results-arranged-by").text(get_item_info_for_display("Results arranged by", "Results not sorted", "#arrange-results-by", "-1"));
}


$("#next_button").click(show_next_ads);
$("#prev_button").click(show_prev_ads);
$("#search-button").click(search_button);
$(document).ready(load_initial_list_of_ads);
