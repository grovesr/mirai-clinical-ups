"use strict";
$(document).ready(function(){
    $("#container").append(saverButton);
    $("#container").append(chooserButton);
});
var chooserOptions = {

    // Required. Called when a user selects an item in the Chooser.
    success: function(files) {
	    var file_string='';
	    // string of returned urls
	    files.forEach(function(filename) {
	        file_string += filename.link + '&';
	    } );// end foreachfunction
	    file_string=file_string.slice(0,-1);
	    $("#id_files").attr("value",file_string);
	    //$("#id_file_url").val(get_args[0]);
	    //$.get("file_selection",{'num_files':files.length});
	    //$("#returned_files").append(get_args);
    }, // success function

    // Optional. Called when the user closes the dialog without selecting a file
    // and does not include any parameters.
    cancel: function() {

    },

    // Optional. "preview" (default) is a preview link to the document for sharing,
    // "direct" is an expiring link to download the contents of the file. For more
    // information about link types, see Link types below.
    linkType: "direct", //"preview", or "direct"

    // Optional. A value of false (default) limits selection to a single file, while
    // true enables multiple file selection.
    multiselect: true // false or true

    // Optional. This is a list of file extensions. If specified, the user will
    // only be able to select files with these extensions. You may also specify
    // file types, such as "video" or "images" in the list. For more information,
    // see File types below. By default, all extensions are allowed.
    //extensions: ['.pdf', '.doc', '.docx'],
};

var saverOptions = {
    files: [
        // You can specify up to 100 files.
        {'url': "http://208.69.32.145/UPS/UpsShipmentOrders/tfile.txt"},
	    {'url': "https://dl.dropboxusercontent.com/s/deroi5nwm6u7gdf/advice.png"}
        // ...
    ], // end file list

    // Success is called once all files have been successfully added to the user's
    // Dropbox, although they may not have synced to the user's devices yet.
    success: function () {},

    // Progress is called periodically to update the application on the progress
    // of the user's downloads. The value passed to this callback is a float
    // between 0 and 1. The progress callback is guaranteed to be called at least
    // once with the value 1.
    progress: function (progress) {},

    // Cancel is called if the user presses the Cancel button or closes the Saver.
    cancel: function () {},

    // Error is called in the event of an unexpected response from the server
    // hosting the files, such as not being able to find a file. This callback is
    // also called if there is an error on Dropbox or if the user is over quota.
    error: function (errorMessage) {
	console.log(errorMessage);
	}
};
var saverButton = Dropbox.createSaveButton(saverOptions);
var chooserButton = Dropbox.createChooseButton(chooserOptions);

