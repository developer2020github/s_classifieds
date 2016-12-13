
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
    //selected_sub_category_id.append($("<option selected disabled/>").val("Select Sub - Category").text("Select Sub - Category"));
    $.each(list_of_selected_sub_categories, function(index, value) {
        selected_sub_category_id.append($("<option />").val(value.id).text(value.name));
    });
}
