var current_ads_idx = 0; 

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

function build_filters(){

    var selected_city = $("#search-city-select").val();
    var selected_category_id  =  $("#category-selected").val();
    var selected_sub_category_id = $("#sub-category-selected").val();
    var select_ads_within_days = $("#select-ads-within-days").val();

    var filters = { "selected_city": selected_city, "selected_category_id" : selected_category_id,
    "selected_sub_category_id" : selected_sub_category_id, "select_ads_within_days" : select_ads_within_days };

    console.log(filters);
}


function search_button(){
    build_filters();   
}


function update_displayed_ads(ads) {
    var selected_ads_id = $("#displayed_ads");
    selected_ads_id.html("");
    //console.log(ads);
    $.each(ads, function(index, value) {
        selected_ads_id.append(value);
    });

    current_ads_idx = current_ads_idx + 10; 
}



function show_next_ads() {
    var request = { "show_next": true, "min_idx" : current_ads_idx};
    var request_url = "/update_ads_list";

    $.ajax({
        dataType: "json",
        url: request_url,
        data: request,
        success: update_displayed_ads
    });


}

$("#next_button").click(show_next_ads);
$("#search-button").click(search_button);

