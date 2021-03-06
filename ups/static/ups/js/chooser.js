"use strict";
$(document).ready(function(){
    //$("#container").append(saverButton);
    $("#container").append(chooserButton);
});
var chooserOptions = {

    // Required. Called when a user selects an item in the Chooser.
    success: function(files) {
	    var fileString='';
	    var fileListItem='';
	    // string of returned urls
	    if (files.length > 0) {
	        $("#file_list").before($("<p></p>").text("List of Selected Files:"));
	        $("#id_files").after($("<input></input>").attr('type="Input"'));
	        $("form").append('<input type="submit" value="Create PickTicket" class="pkt-button">');
	        $(".dropbox-dropin-btn").hide();
	    }
	    files.forEach(function(filename) {
	        // create ampersand separated list of URLs
	        fileString += filename.link + '&';
	        // display the URLs
	        fileListItem=$("<li></li>").text(filename.link);
	        $("#file_list").append(fileListItem);
	    } );// end foreachfunction
	    // strip off the final ampersand
	    fileString=fileString.slice(0,-1);
	    // set the hidden form element value so we can submit it
	    $("#id_files").attr("value",fileString);	    
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

