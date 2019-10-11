// utility functions
$.ajaxSetup({ cache: false }); // ie9 fix
//if(/MSIE \d/.test(navigator.userAgent))
//        document.write('<script src="/static/assets/js/jquery.xdomainrequest.min.js"><\/script>');
// debounce delays firing of functions - typically used with resize events
// ---------------------------------------------------------------
function debounce(func, wait, immediate) {
     var timeout;
     return function() {
          var context = this, args = arguments;
          var later = function() {
               timeout = null;
               if (!immediate) func.apply(context, args);
          };
          var callNow = immediate && !timeout;
          clearTimeout(timeout);
          timeout = setTimeout(later, wait);
          if (callNow) func.apply(context, args);
     };
}
// draws triangle skew in top of header
// redraws with every resize
// ---------------------------------------------------------------
function resize_skew_div(){
	$("#header-skew-login").html("");
	var div_w = $("#header-skew-login").width();
	var div_h = $("#header-skew-login").height();
	var header_svg = SVG("header-skew-login").size(div_w, div_h);
    	header_svg.polygon("0,0 "+div_w+",0 0,"+div_h).fill("#fff").stroke({ width: 0 });
    	//
    	$("#header-skew-application").html("");
	var div_w = $("#header-skew-application").width();
	var div_h = $("#header-skew-application").height();
	var header_svg = SVG("header-skew-application").size(div_w, div_h);
    	header_svg.polygon("0,0 "+div_w+",0 0,"+div_h).fill("#fff").stroke({ width: 0 });
    	//
    	$("#header-skew-profile").html("");
	var div_w = $("#header-skew-profile").width();
	var div_h = $("#header-skew-profile").height();
	var header_svg = SVG("header-skew-profile").size(div_w, div_h);
    	header_svg.polygon("0,0 "+div_w+",0 0,"+div_h).fill("#fff").stroke({ width: 0 });
    	//
    	$("#header-skew-create").html("");
	var div_w = $("#header-skew-create").width();
	var div_h = $("#header-skew-create").height();
	var header_svg = SVG("header-skew-create").size(div_w, div_h);
    	header_svg.polygon("0,0 "+div_w+",0 0,"+div_h).fill("#fff").stroke({ width: 0 });
}
window.addEventListener('resize', resize_skew_div);
function numberWithCommas(x){
	var parts = x.toString().split(".");
	parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	return parts.join(".");
}

// main script loop
// ---------------------------------------------------------------
$( document ).ready(function() {
	// bootstrap bug fix for having padding-right linger from closed modal
	$(document.body).on("hidden.bs.modal", function(){
	    $('body').css('padding-right','0');
	});
	// resize circuit to fit aspect ratio of page
     resize_skew_div();
	$("body").tooltip({
	    selector: "[data-toggle=tooltip]"
	});
	// ---------------------------------------------------------------
	// duplicate prior art field in step 1
	// ---------------------------------------------------------------
	$(document.body).on("click", "#duplicate-knownart", function(){
		var knownart_num = $(".knownart-row",".knownart-holder").length;
		if ( knownart_num < 20){
			knownart_id = knownart_num + 1;
			$(".knownart-holder").append("<div class='form-group'><div class='knownart-row flex-row top' id='knownart-row-" + knownart_id + "'><div class='knownart-row-field-holder'><input type='text' class='form-control knownart-field' id='patent_" + knownart_id +"' name='patent_" + knownart_id +"' value='' style='margin-top:.25em;margin-bottom:.25em;'><div class='help-block with-errors'></div></div><div><div class='hex-button-small nlp-bluegray remove-knownart' style='margin-top:.25em;margin-bottom:.25em;'><button type='button' class='btn btn-primary'><div class='icon nlpapp-icon-minus'></div></button></div></div></div></div>");
		}
		if ( $(".knownart-row",".knownart-holder").length == 20 ){
			$(this).addClass("disabled");
		}
	});
	// remove key elements delegated click
	$(document.body).on("click", ".remove-knownart", function(){
		$(this).parent().parent().remove();
		$("#duplicate-knownart").removeClass("disabled");
	});
	// ---------------------------------------------------------------
	// back to step 2 from step 2a
	// ---------------------------------------------------------------
	$( "#back_step2" ).click(function() {
		console.log("back to step 2 button click");
		nlp_router.navigate("#step2_interim");
	});
	$( ".navigate_step2a" ).click(function() {
		console.log("back to step 2a button click");
		nlp_router.navigate("#step2a_interim");
	});

	
	// ---------------------------------------------------------------
	// duplicate key elements field in step 3
	// ---------------------------------------------------------------
	$(document.body).on("click", "#duplicate-keyelement", function(){
		var keyelement_num = $(".keyelement-row","#keyelement-holder").length;
		if ( keyelement_num < 5){
			keyelement_id = keyelement_num + 1;
			$("#keyelement-holder").append("<div class='form-group'><div class='keyelement-row flex-row top' id='keyelement-row-" + keyelement_id + "'><div class='keyelement-row-field-holder'><input type='text' class='form-control keyelement-field' id='element_" + keyelement_id +"' name='element_" + keyelement_id +"' value='' style='margin-top:.25em;margin-bottom:.25em;'><div class='help-block with-errors'></div></div><div><div class='hex-button-small nlp-bluegray remove-keyelement' style='margin-top:.25em;margin-bottom:.25em;'><button type='button' class='btn btn-primary'><div class='icon nlpapp-icon-minus'></div></button></div></div></div></div>");
		}
		if ( $(".keyelement-row","#keyelement-holder").length == 5 ){
			$(this).addClass("disabled");
		}
	});
	// remove key elements delegated click
	$(document.body).on("click", ".remove-keyelement", function(){
		$(this).parent().parent().remove();
		$("#duplicate-keyelement").removeClass("disabled");
	});

	// function to check tables and turn on/off empty row notification
	// used by both add to saved and delete from results functions above
	// -----------------------------------------------------------------------------------------
	function check_priorart_table(table){
		var emptymsg_visible = $(".empty-row-message","#"+table).is(":visible");
		if ( $("tr:visible","#"+table+" tbody").length > 1 ){
			if(emptymsg_visible){
				// hide
				$(".empty-row-message","#"+table).css("display","none");
			}
		} else if( $("tr:visible","#"+table+" tbody").length < 1 ){
			// hide
			$(".empty-row-message","#"+table).show(200);
		}
	}

	// ---------------------------------------------------------------
	// filters button toggles
	// ---------------------------------------------------------------
	$( "#nlpapp_showfilters" ).click(function() {
		$("#nlpapp-filters").fadeIn(200);
		$("#nlpapp_showfilters").parent().hide();
		$("#nlpapp_hidefilters").parent().show();
	});
	$( "#nlpapp_hidefilters" ).click(function() {
		$("#nlpapp-filters").fadeOut(200);
		$("#nlpapp_showfilters").parent().show();
		$("#nlpapp_hidefilters").parent().hide();
	});

	// loader animation
	// ---------------------------------------------------------------
	var animspeed = 150;
	var $loader_hexhead = $("#loader-hexhead");
	function loopanimation(loader_hexhead_id){
		loader_hexhead_id.velocity({ translateX:-14.286,translateY:24.666 }, { duration : animspeed, easing: "linear", complete: function() {
			loader_hexhead_id.velocity({ translateX:-42.857,translateY:24.666 }, { duration : animspeed, easing: "linear", complete: function() {
				loader_hexhead_id.velocity({ translateX:-57.143,translateY:0 }, { duration : animspeed, easing: "linear", complete: function() {
					loader_hexhead_id.velocity({ translateX:-85.714,translateY:0 }, { duration : animspeed, easing: "linear", complete: function() {
						loader_hexhead_id.velocity({ translateX:-100,translateY:24.666 }, { duration : animspeed, easing: "linear", complete: function() {
							loader_hexhead_id.velocity({ translateX:-85.714,translateY:49.333 }, { duration : animspeed, easing: "easlineareInOut", complete: function() {
								loader_hexhead_id.velocity({ translateX:-57.143,translateY:49.333 }, { duration : animspeed, easing: "linear", complete: function() {
									loader_hexhead_id.velocity({ translateX:-42.857,translateY:24.667 }, { duration : animspeed, easing: "linear", complete: function() {
										loader_hexhead_id.velocity({ translateX:-57.143,translateY:0 }, { duration : animspeed, easing: "linear", complete: function() {
											loader_hexhead_id.velocity({ translateX:-42.857,translateY:-24.667 }, { duration : animspeed, easing: "linear", complete: function() {
												loader_hexhead_id.velocity({ translateX:-14.286,translateY:-24.667 }, { duration : animspeed, easing: "linear", complete: function() {
													loader_hexhead_id.velocity({ translateX:0,translateY:0 }, { duration : animspeed, easing: "linear", complete: function(){
														loopanimation(loader_hexhead_id)
													}});
												}});
											}});
										}});
									}});
								}});
							}});
						}});
					}});
				}});
			}});
		}});
	}
	var $loader_hexh1 = $("#loader-hexhead");
	loopanimation( $loader_hexh1 );

	// ---------------------------------------------------------------
	// ---------------------------------------------------------------
	// Data Loading & Objects
	// ---------------------------------------------------------------
	// ---------------------------------------------------------------

	var nlpapp_dataobject = {
		user : {
			email		: "",
			first_name	: "",
			last_name		: "",
			organization	: "",
			client 		: "",
			role 		: "",
			admin 		: "",
			country 		: "",
			region 		: "",
			update_cost 	: "",
			search_cost 	: "",
			payment_expiry : "",
			payment_number	: "",
			payment_method	: "",
			stripe_key 	: ""
		},
		current_project  : {
			name			: "",
			last_edited	: "",
			progress		: "",
			secure		: "",
			cpc_class	: "",
			cpc_section	: "",
			cpc_classes 	: "",
			priorart_page : ""
		},
		security_unlocked : 0
	};
	var nlpapp_root_message = [];
	// route defintions
	// ---------------------------------------------------------------
	var nlpapp_dataroute_user = "data/nlpapp_data.json";

	var nlp_dataroute = {
		login 					: "https://www.nlpatent.com/login",
		signup 					: "https://www.nlpatent.com/addtrial",
		logout 					: "https://www.nlpatent.com/logout",
		forgotpassword				: "https://www.nlpatent.com/recoverpassword",
		step1_submit 				: "https://www.nlpatent.com/submitstep1dataX",
		step2b_submit 				: "https://www.nlpatent.com/submitstep2dataX",
		current_project_submit 		: "https://www.nlpatent.com/setcurrentproject",
		add_project_submit 			: "https://www.nlpatent.com/addproject",
		remove_project_submit 		: "https://www.nlpatent.com/removeproject",
		rename_project_submit 		: "https://www.nlpatent.com/renameproject",
		setproject_security_submit	: "https://www.nlpatent.com/setprojectsecurity",
		step1_load 					: "https://www.nlpatent.com/getstep1dataX",
		step2_load 					: "https://www.nlpatent.com/getstep2classesX",
		step2a_load 				: "https://www.nlpatent.com/getstep2classesX",
		step2b_load 				: "https://www.nlpatent.com/getstep2subclasses",
		step3_results_load 			: "https://www.nlpatent.com/getstep3resultsX",
		step3_savedresults_load		: "https://www.nlpatent.com/getstep3saved",
		step3_download_all	 		: "https://www.nlpatent.com/downloadallresults",
		step3_download_saved	 	: "https://www.nlpatent.com/downloadsavedresults",
		step3_save_result 			: "https://www.nlpatent.com/saveresult",
		step3_remove_result 		: "https://www.nlpatent.com/removeresult",
		step3_delete_result 		: "https://www.nlpatent.com/deleteresult",
		step3_save_result_manual	: "https://www.nlpatent.com/saveresultmanual",
		apply_filters_submit 		: "https://www.nlpatent.com/applyfiltersX",
		update_results_submit 		: "https://www.nlpatent.com/updateresultsX",
		clearupdate_results_submit 	: "https://www.nlpatent.com/clearupdatedX",
		step3_submit 				: "https://www.nlpatent.com/submitstep3data",
		step4_load 				: "https://www.nlpatent.com/getstep4results",
		analysis_email 			: "https://www.nlpatent.com/emailresults",
		analysis_download 			: "https://www.nlpatent.com/downloadresults",
		edit_profile_submit 		: "https://www.nlpatent.com/updatepersonal",
		change_password_submit 		: "https://www.nlpatent.com/changepassword",
		profile_load 				: "https://www.nlpatent.com/getprofileinfo",
		planinfo_load 				: "https://www.nlpatent.com/getprofileinfo",
		change_payment 			: "https://www.nlpatent.com/changepayment",
		currentusage_load			: "https://www.nlpatent.com/getcurrentusage",
		useraccounts_load 			: "https://www.nlpatent.com/getuseraccounts",
		capusage_set 				: "https://www.nlpatent.com/changecap",
		current_project_load 		: "https://www.nlpatent.com/getcurrentproject",
		all_projects_load 			: "https://www.nlpatent.com/getallprojects",
		get_abstract				: "https://www.nlpatent.com/getresultdetails"
	}

	// these are listeners for the loader modal show/hide events
	// with multiple modals we have to push any other open
	// models behind z-index 1040 (where the backdrop resides)
	$('#nlpapp-loader').on('show.bs.modal', function () {
		$('#nlpapp-modal-edit-project').css('z-index', 1039);
		$('#nlpapp-modal-delete-priorartresult').css('z-index', 1039);
		$('#nlpapp-modal-delete-savedpriorart').css('z-index', 1039);
		$('#nlpapp_forgotpassword_modal').css('z-index', 1039);
	});

	$('#nlpapp-loader').on('hidden.bs.modal', function () {
		$('#nlpapp-modal-edit-project').css('z-index', 1041);
		$('#nlpapp-modal-delete-priorartresult').css('z-index', 1041);
		$('#nlpapp-modal-delete-savedpriorart').css('z-index', 1041);
		$('#nlpapp_forgotpassword_modal').css('z-index', 1041);
	});

	function nlpapp_hide_loader_modal(){
		if ( $('#nlpapp-loader').is(':visible') ){
			$('#nlpapp-loader').modal('hide');
		}
	}
	function nlpapp_show_loader_modal(message){
		if ( message == "" || !message ){
			message = "PROCESSING...";
		}
		$("#nlpapp-loader").find(".nlpapp-loader-message").text(message);
		if ( !$('#nlpapp-loader').is(':visible') ){
			$('#nlpapp-loader').modal('show');
		}
	}
	$(document).on('show.bs.modal', '.modal', function () {
		// if we have modals calling other modals (e.g. a load/error modal over a edit project)
		// we hide the other modal backdrop
		if ($(".modal-backdrop").length > 0) {
			$(".modal-backdrop").not(':first').modal("removeBackdrop");
		}
	});
	function nlpapp_check_root_message(){
		if ( nlpapp_root_message.length ){
			$( nlpapp_root_message[0], nlpapp_root_message[1] ).addClass(nlpapp_root_message[2]).text(nlpapp_root_message[3]).show();
			nlpapp_root_message = [];
		}
	}

	var cpc_sections=["","A | Human Necessities","B | Operations; Transporting","C | Chemistry; Metallurgy","D | Textiles; Paper","E | Fixed Constructions","F | Mechanical Engineering; Lighting; Heating; Weapons; Blasting","G | Physics","H | Electricity"];
	var cpc_section_codes=["","A","B","C","D","E","F","G","H"];

	// ---------------------------------------------------------------
	// ---------------------------------------------------------------
	// form listeners
	// ---------------------------------------------------------------
	// ---------------------------------------------------------------
	//  Forgot password
	// ---------------------------------------------------------------
	$( "#nlpapp_forgotpassword" ).submit(function(event) {
		event.preventDefault();
		validate_forgotpassword_form = nlpapp_validate_form_forgotpassword();
		if ( validate_forgotpassword_form === true ){
			var form_data = "email=" + $("#forgotpassword_email","#nlpapp_forgotpassword").val();
			// post data
			ajaxCall( nlp_dataroute.forgotpassword , "POST", form_data, nlpapp_forgotpassword_complete, "#nlpapp_forgotpassword");
		}
	});
	function nlpapp_forgotpassword_complete(data){
		var response_msg = Object.keys(data)[0];
		if ( response_msg == "ERROR" ){
			$(".help-block","#nlpapp_forgotpassword").addClass("with-errors").html( data[Object.keys(data)[0]] ).show();
		} else {
			$(".help-block","#nlpapp_forgotpassword").removeClass("with-errors").html( data[Object.keys(data)[0]] ).show();
		}
		nlpapp_hide_loader_modal();
	}
	$('#nlpapp_forgotpassword_modal').on('hidden.bs.modal', function (e) {
		$("input[type=text],select","#nlpapp_forgotpassword_modal").val("");
		$(".help-block","#nlpapp_forgotpassword_modal").text("");
	});


	// ---------------------------------------------------------------
	//  Signup
	// ---------------------------------------------------------------
	$( "#nlpapp_signup" ).submit(function(event) {
		event.preventDefault();
		validate_signup_form = nlpapp_validate_form_signup();
		if ( validate_signup_form === true ){
			form_data = "name=" + $("#signup_name","#nlpapp_signup").val() + "&email=" + $("#signup_email","#nlpapp_signup").val() + "&signup_referral=" + $("#signup_referral","#nlpapp_signup").val();
			if ( $("#signup_referral_other","#nlpapp_signup").val() !== ""){
				form_data = form_data + "&signup_referral_other=" + $("#signup_referral_other","#nlpapp_signup").val();
			}
			// post data
			ajaxCall( nlp_dataroute.signup , "POST", form_data, nlpapp_signup_complete, "#nlpapp_signup");
		}
	});
	function nlpapp_signup_complete(data){
		$(".form-feedback","#nlpapp_login_signup_div").addClass("SUCCESS").text("You have been added to the list.").show();
		$('#nlpapp_signup_modal').modal('hide');
		nlpapp_hide_loader_modal();
	}
	$('#nlpapp_signup_modal').on('hidden.bs.modal', function (e) {
		$("input[type=text],select","#nlpapp_signup_modal").val("");
		$("#signup_referral_other","#nlpapp_signup_modal").parent().parent().hide();
		$(".help-block","#nlpapp_signup_modal").text("");
	});

	// ---------------------------------------------------------------
	//  logout
	// ---------------------------------------------------------------
	function nlpapp_logout(){
		ajaxCall( nlp_dataroute.logout , "GET", "", nlpapp_logout_complete, "#nlpapp_login", null);
	}
	function nlpapp_logout_complete(){
		nlpapp_root_message = [".form-feedback","#nlpapp_login","SUCCESS","You have successfully logged out." ];
		// navigation to login
		nlp_router.navigate("");
	}
	// ---------------------------------------------------------------
	//  login
	// ---------------------------------------------------------------
	$( "#nlpapp_login" ).submit(function(event) {
		event.preventDefault();
		validate_login_form = nlpapp_validate_form_login();
		if ( validate_login_form === true ){
			var form_data = ajaxSerializeForm("#nlpapp_login");
			// post data
			ajaxCall( nlp_dataroute.login , "POST", form_data, nlpapp_login_setdata, "#nlpapp_login", nlpapp_login_complete, "");
		}
	});
	function nlpapp_login_complete(){
		nlpapp_load_profile();
	}
	// ---------------------------------------------------------------
	//  unlock step 1 description
	// ---------------------------------------------------------------
	$( "#nlpapp_step1_unlock" ).submit(function(event) {
		event.preventDefault();
		validate_unlock_form = nlpapp_validate_form_unlockstep1();
		if ( validate_unlock_form === true ){
			// console.log ("nlpapp_login form submit");
			var form_data = "email="+ nlpapp_dataobject.user.email +"&password=" + $("#unlock_password","#nlpapp_step1_unlock").val() ;
			// post data
			ajaxCall( nlp_dataroute.login , "POST", form_data, nlpapp_unlockstep1_complete, "#nlpapp_step1_unlock", null);
		}
	});
	function nlpapp_unlockstep1_complete(data){
		nlpapp_dataobject.security_unlocked = 1;
		nlp_router.navigate("#step1");
	}

	// ---------------------------------------------------------------
	// load profile
	// ---------------------------------------------------------------
	function nlpapp_load_profile(){
		ajaxCall( nlp_dataroute.profile_load, "GET", "", nlpapp_load_profile_setdata, "application", nlpapp_load_profile_complete, "");
	}
	function nlpapp_load_profile_complete(data){
		$(".row-header-welcome").text("Welcome back, " + nlpapp_dataobject.user.first_name );
		nlpapp_load_currentproject();
		// if user is administrator, load Stripe scripts so we have them in place
		if ( nlpapp_dataobject.user.admin === 1){
			$.getScript( "https://checkout.stripe.com/checkout.js" )
				.done(function( script, textStatus ) {
					console.log("Stripe script load succeeded.");
				})
				.fail(function( jqxhr, settings, exception ) {
				console.log("Stripe script load failed.");
			});
		}
	}
	// ---------------------------------------------------------------
	// load current project
	// ---------------------------------------------------------------
	function nlpapp_load_currentproject(){
		ajaxCall( nlp_dataroute.current_project_load, "GET", "", nlpapp_load_currentproject_setdata, "application", nlpapp_load_currentproject_complete, "");
	}
	function nlpapp_load_currentproject_complete(){
		if( nlpapp_dataobject.current_project.name !== ""){
			// call utility route to change project
			nlp_router.navigate("#change_project?newproject=true");
		} else {
			// there is no current project
			nlp_router.navigate("#create_project");
		}
	}
	// ---------------------------------------------------------------
	// step one load & setup
	// ---------------------------------------------------------------
	function nlpapp_load_stepone(){
		nlapp_reset_ui();
		ajaxCall( nlp_dataroute.step1_load, "GET", "", nlpapp_load_stepone_complete, "application", null);
	}
	function nlpapp_load_stepone_complete(data,callback){
	    $("#priority_date","#nlpapp_step_one_form").datepicker();
	    $("#priority_date","#nlpapp_step_one_form").datepicker("option","dateFormat","yy-mm-dd");
		// reset ui
		$("#cpc_section","#nlpapp_step_one_form").val("1");
		$("#keyelement-holder .form-group:not(:first-child)").remove();
		$("#duplicate-keyelement","#nlpapp_step_one_form").removeClass("disabled");
		$("#priority_date","#nlpapp_step_one_form").datepicker("setDate", null);
		// set values
		$("#description","#nlpapp_step_one_form").val(data.description); // set description text
		//if (data.cpc_section !== null){
		//	$("#cpc_section","#nlpapp_step_one_form").val(data.cpc_section);
		//}
		$("#element_1","#nlpapp_step_one_form").val("");
		console.log(data.known_prior_art);

		$(".knownart-holder","#nlpapp_step_one_form").html("<div class='form-group'><div class='knownart-row flex-row top' id='knownart-row-1'><div class='knownart-row-field-holder'><input type='text' class='form-control knownart-field' id='patent_1' name='patent_1' value='' style='margin-top:.25em;margin-bottom:.25em;'><div class='help-block with-errors'></div></div><div><div class='hex-button-small nlp-orange' id='duplicate-knownart' style='margin-top:.25em;margin-bottom:.25em;'><button type='button' class='btn btn-primary'><div class='icon nlpapp-icon-plus'></div></button></div></div></div></div>");

		if( data.known_prior_art ){
			//$("#element_1","#nlpapp_step_one_form").val("");
			//$("#element_2,#element_3,#element_4,#element_5","#nlpapp_step_one_form").remove();
			//$("input[type=text]","#nlpapp_step_one_form").val("");
			$(".help-block,.form-feedback","#nlpapp_step_one_form").text("");
			$(".form-feedback","#nlpapp_step_one_form").hide();
			console.log(data.known_prior_art.length);
			for(i=0;i<data.known_prior_art.length;i++){
				if (i == 0){
					$("#patent_1","#nlpapp_step_one_form").val( data.known_prior_art[i] );
				} else {
					$(".knownart-holder","#nlpapp_step_one_form").append("<div class='form-group'><div class='knownart-row flex-row top' id='knownart-row-" + (i+1) + "'><div class='knownart-row-field-holder'><input type='text' class='form-control knownart-field' id='patent_" + (i+1) +"' name='patent_" + (i+1) +"' value='" + data.known_prior_art[i] + "' style='margin-top:.25em;margin-bottom:.25em;'><div class='help-block with-errors'></div></div><div><div class='hex-button-small nlp-bluegray remove-knownart' style='margin-top:.25em;margin-bottom:.25em;'><button type='button' class='btn btn-primary'><div class='icon nlpapp-icon-minus'></div></button></div></div></div></div>");
				}
			}
			if(data.known_prior_art.length == 20){
				$("#duplicate-knownart","#nlpapp_step_one_form").addClass("disabled");
			}
		}
		if (data.priority_date !== null){
            $("#priority_date","#nlpapp_step_one_form").datepicker("setDate", data.priority_date);
            $("#priority_date","#nlpapp_step_one_form").datepicker("refresh");
		}
		nlpapp_hide_loader_modal();
	}
	// ---------------------------------------------------------------
	// step one submission & next step
	// ---------------------------------------------------------------
	$( "#nlpapp_step_one_form" ).submit(function(event) {
		event.preventDefault();
		validate_step_one_form = nlpapp_validate_form_stepone();
		if ( validate_step_one_form === true ){
			// set cpc section
			//nlpapp_dataobject.current_project.cpc_section = cpc_sections[ $("#cpc_section","#nlpapp_step_one_form").val() ];
			nlpapp_dataobject.current_project.cpc_section = 1;
			var form_data = $("select,textarea,input","#nlpapp_step_one_form").filter(function() { return $(this).val(); }).serialize();
			// check date selected, and if not null append it to form_data string
			var temp_priority_date = $("#priority_date","#nlpapp_step_one_form").datepicker("getDate");
			if( temp_priority_date !== null ){
				priority_date_data = $.datepicker.formatDate("yy-mm-dd", temp_priority_date);
				form_data = form_data + "&priority_date="+priority_date_data;
			}
			// post data
			ajaxCall( nlp_dataroute.step1_submit, "POST", form_data, nlpapp_submit_stepone_complete, "#nlpapp_step_one_form", null, "ASSESSING INPUT... THIS MIGHT TAKE A MINUTE");
		}
	});
	function nlpapp_submit_stepone_complete(data,callback){
		nlpapp_verify_currentproject_progress();
	}

	// ---------------------------------------------------------------
	// check progress in getcurrentproject
	// ---------------------------------------------------------------
	function nlpapp_verify_currentproject_progress(){
	    $.ajax({
			url: nlp_dataroute.current_project_load,
			type: "GET",
			data: "",
			dataType: 'json',
			success: function(response_data) {
			  if(response_data.progress){
			    if( response_data.progress == 3){
        	        nlpapp_dataobject.current_project.progress = 3;
        	        nlpapp_set_progress_tabs(3);
        	        //nlp_router.navigate("#step2a");
					nlp_router.navigate("#step2");
        	    } else {
        	        nlpapp_set_progress_tabs(2);
        	        //nlp_router.navigate("#step2a");
					nlp_router.navigate("#step2");
        	    }
			  }
			}
	    });
	}



	// step two - select technology area click events
	// ---------------------------------------------------------------
	$("input[type='checkbox']","#nlpapp-technologyclasses-table").change(function() {
		var checked_technologyarea = $(this).val();
		if(this.checked) {
			console.log("technology " + checked_technologyarea + " area checked");
			
			//
			$("tr","#nlpapp-technologyclasses-table tbody").not("#technologyarea_"+checked_technologyarea).addClass("disabled");
			$("tr","#nlpapp-technologyclasses-table tbody").not("#technologyarea_"+checked_technologyarea).find("input[type='checkbox']").attr("disabled", true);
		} else {
			console.log("technology " + checked_technologyarea + " area unchecked");
			$("tr","#nlpapp-technologyclasses-table tbody").not("#technologyarea_"+checked_technologyarea).removeClass("disabled");
			$("tr","#nlpapp-technologyclasses-table tbody").not("#technologyarea_"+checked_technologyarea).find("input[type='checkbox']").removeAttr("disabled");
		}
	});
	
	

	// ---------------------------------------------------------------
	// step two - load & setup
	// ---------------------------------------------------------------
	function nlpapp_load_steptwo(){
		nlapp_reset_ui();
		///ajaxCall( nlp_dataroute.step2_load, "GET", "", nlpapp_load_steptwo_complete, "application", null, "ASSESSING INPUT... THIS MIGHT TAKE A MINUTE");
		nlpapp_load_steptwo_complete("","");
	}
	function nlpapp_load_steptwo_complete(data,callback){
		// reset UI
		//$("tbody","#nlpapp-technologyclasses-table").html("");
		var cpcclasses_selected = $('#nlpapp-technologyclasses-table input:checked').length > 0
		if ( cpcclasses_selected ){
			$("button[type=submit]","#nlpapp_step_two_form").parent().removeClass("disabled");
		} else {
			$("button[type=submit]","#nlpapp_step_two_form").parent().addClass("disabled");
		}

		// needs to be updated for loading technology areas
		// insert cpc classes to table
		//$(".nlpapp_project_cpc_section").text( cpc_sections[data.cpc_section] );
		// for(i=0;i<data.cpc_classes.length;i++){
		// 	$("tbody","#nlpapp-technologyclasses-table").append("<tr><td scope='row'><div class='checkbox'><label><input type='checkbox' value='" + data.cpc_classes[i].n + "' name='class_select' data-display='" + data.cpc_classes[i].n + " | " + data.cpc_classes[i].t + "'><span class='cr'><div class='icon nlpapp-icon-check'></div></span>" + data.cpc_classes[i].n + "</label></div></td><td>" + data.cpc_classes[i].p + "</td><td>" + data.cpc_classes[i].t + "</td></tr>");
		// }
		// bind click events for these newly added radios
		$("#nlpapp-technologyclasses-table").find(":checkbox").bind('change', function(){
			var cpcclasses_selected = $('#nlpapp-technologyclasses-table input:checked').length > 0
			if ( cpcclasses_selected ){
				$("button[type=submit]","#nlpapp_step_two_form").parent().removeClass("disabled");
			} else {
				$("button[type=submit]","#nlpapp_step_two_form").parent().addClass("disabled");
			}
		});
		nlpapp_hide_loader_modal();
	}
	// ---------------------------------------------------------------
	// step two - submission & next step
	// ---------------------------------------------------------------
	$( "#nlpapp_step_two_form" ).submit(function(event) {
		event.preventDefault();
		if ( !$("button[type=submit]","#nlpapp_step_two_form").parent().hasClass("disabled") ){
			var form_data = "cpc_section=";
			var cpc_classes_display = "";
			var temp = $('#nlpapp-technologyclasses-table input:checked');
			console.log( "value is " + temp );
			//$('#nlpapp-technologyclasses-table input:checked').val();
			form_data = form_data + $('#nlpapp-technologyclasses-table input:checked').val();
			nlpapp_dataobject.current_project.cpc_class = $('#nlpapp-technologyclasses-table input:checked').val();
			//$("input[name=class_select]:checked","#nlpapp-cpcclasses-table").each(function() {
			//	form_data = form_data + $(this).attr("value") + ",";
			cpc_classes_display = cpc_classes_display + $(this).attr("data-display") + "<br>";
			//});
			//form_data = form_data.slice(0, -1);
			nlpapp_dataobject.current_project.cpc_classes = cpc_classes_display;
			// post data
			ajaxCall( nlp_dataroute.step2a_load, "POST", form_data, nlpapp_load_steptwo_a_complete , "#nlpapp_step_two_form", null, "PROCESSING...");
		}
	});
	function nlpapp_submit_steptwo_complete(data,callback){
		// pass steptwo_a data
		nlpapp_load_steptwo_a(data);
	}


	// ---------------------------------------------------------------
	// step two - part a load & setup
	// ---------------------------------------------------------------
	function nlpapp_load_steptwo_a(data){
		var form_data = "cpc_section=" + nlpapp_dataobject.current_project.cpc_class;
		nlapp_reset_ui();
		show_application_page("application","step2a");
		ajaxCall( nlp_dataroute.step2a_load, "POST", form_data, nlpapp_load_steptwo_a_complete, "application", null, "ASSESSING INPUT... THIS MIGHT TAKE A MINUTE");
	}
	function nlpapp_load_steptwo_a_complete(data,callback){
		nlapp_reset_ui();
		show_application_page("application","step2a");
		// reset UI
		$("tbody","#nlpapp-cpcclasses-table").html("");
		$("button[type=submit]","#nlpapp_step_twoa_form").parent().addClass("disabled");
		// insert cpc classes to table
		$(".nlpapp_project_cpc_section").text( cpc_sections[data.cpc_section] );
		for(i=0;i<data.cpc_classes.length;i++){
			$("tbody","#nlpapp-cpcclasses-table").append("<tr><td scope='row'><div class='checkbox'><label><input type='checkbox' value='" + data.cpc_classes[i].n + "' name='class_select' data-display='" + data.cpc_classes[i].n + " | " + data.cpc_classes[i].t + "'><span class='cr'><div class='icon nlpapp-icon-check'></div></span>" + data.cpc_classes[i].n + "</label></div></td><td>" + data.cpc_classes[i].p + "</td><td>" + data.cpc_classes[i].t + "</td></tr>");
		}
		// bind click events for these newly added radios
		$("#nlpapp-cpcclasses-table").find(":checkbox").bind('change', function(){
			var cpcclasses_selected = $('#nlpapp-cpcclasses-table input:checked').length > 0
			if ( cpcclasses_selected ){
				$("button[type=submit]","#nlpapp_step_twoa_form").parent().removeClass("disabled");
			} else {
				$("button[type=submit]","#nlpapp_step_twoa_form").parent().addClass("disabled");
			}
		});
		nlpapp_hide_loader_modal();
	}
	// ---------------------------------------------------------------
	// step two - part a submission & next step
	// ---------------------------------------------------------------
	$( "#nlpapp_step_twoa_form" ).submit(function(event) {
		event.preventDefault();
		if ( !$("button[type=submit]","#nlpapp_step_twoa_form").parent().hasClass("disabled") ){
			var form_data = "cpc_classes=";
			var cpc_classes_display = "";
			$("input[name=class_select]:checked","#nlpapp-cpcclasses-table").each(function() {
				form_data = form_data + $(this).attr("value") + ",";
				cpc_classes_display = cpc_classes_display + $(this).attr("data-display") + "<br>";
			});
			form_data = form_data.slice(0, -1);
			nlpapp_dataobject.current_project.cpc_classes = cpc_classes_display;
			// post data
			ajaxCall( nlp_dataroute.step2b_load, "POST", form_data, nlpapp_submit_steptwo_a_complete , "#nlpapp_step_twoa_form", null, "PROCESSING...");
		}
	});
	function nlpapp_submit_steptwo_a_complete(data,callback){
		// pass steptwo_b data
		nlpapp_load_steptwo_b_complete(data);
	}
	// ---------------------------------------------------------------
	// step two - part b load & setup
	// ---------------------------------------------------------------
	function nlpapp_load_steptwo_b_complete(data){
		// reset UI
		nlapp_reset_ui();
		$("button[type=submit]","#nlpapp_step_twob_form").parent().addClass("disabled");
		$("tbody","#nlpapp-cpcsubclasses-table").html("");
		show_application_page("application","step2b");
		// insert displays for section & classes
		$(".nlpapp_project_cpc_section").text( cpc_sections[data.cpc_section] );
		$(".nlpapp_project_cpc_class").html( nlpapp_dataobject.current_project.cpc_classes );
		//
		for(i=0;i<data.cpc_subclasses.length;i++){
			$("tbody","#nlpapp-cpcsubclasses-table").append("<tr><td scope='row'><div class='checkbox'><label><input type='checkbox' value='" + data.cpc_subclasses[i].n + "' name='class_select'><span class='cr'><div class='icon nlpapp-icon-check'></div></span><a href='https://www.cooperativepatentclassification.org/cpc/definition/" + cpc_section_codes[data.cpc_section] + "/definition-" + data.cpc_subclasses[i].n + ".pdf' target='_blank'>" + data.cpc_subclasses[i].n + "</a></label></div></td><td>" + data.cpc_subclasses[i].p + "</td><td>" + data.cpc_subclasses[i].t + "</td></tr>");
		}
		// bind click events for these newly added radios
		$("#nlpapp-cpcsubclasses-table").find(":checkbox").bind('change', function(){
			var cpcclasses_selected = $('#nlpapp-cpcsubclasses-table input:checked').length > 0;
			if ( cpcclasses_selected ){
				$("button[type=submit]","#nlpapp_step_twob_form").parent().removeClass("disabled");
			} else {
			    $("button[type=submit]","#nlpapp_step_twob_form").parent().addClass("disabled");
			}
			// detect and limit maximum of 5
			var num_subclasses = $('#nlpapp-cpcsubclasses-table input:checked').length;
			console.log(num_subclasses);
			if (num_subclasses <=4){
				// re-enable all not selected
				$("#nlpapp-cpcsubclasses-table input:not(:checked)").parent().parent().parent().parent().removeClass("disabled");
				$("#nlpapp-cpcsubclasses-table input:not(:checked)").removeAttr("disabled");
			} else {
				// disable all not selected
				$("#nlpapp-cpcsubclasses-table input:not(:checked)").parent().parent().parent().parent().addClass("disabled");
				$("#nlpapp-cpcsubclasses-table input:not(:checked)").attr("disabled", true);
			}
		});
		nlpapp_hide_loader_modal();
	}
	// ---------------------------------------------------------------
	// step two - part b submission & next step
	// ---------------------------------------------------------------
	$( "#nlpapp_step_twob_form" ).submit(function(event) {
		event.preventDefault();
		if ( !$("button[type=submit]","#nlpapp_step_twob_form").parent().hasClass("disabled") ){
			var form_data = "cpc_subclasses=";
			$("input[name=class_select]:checked","#nlpapp-cpcsubclasses-table").each(function() {
				form_data = form_data + $(this).attr("value") + ",";
			});
			// post data
			ajaxCall( nlp_dataroute.step2b_submit, "POST", form_data, nlpapp_submit_steptwo_b_complete, "#nlpapp_step_twob_form", null, "SEARCHING FOR PRIOR ART... THIS MIGHT TAKE A MINUTE");
		}
	});
	function nlpapp_submit_steptwo_b_complete(data){
		nlpapp_set_progress_tabs(3);
		nlp_router.navigate("#step3");
	}
	// ---------------------------------------------------------------
	// step three load & setup
	// ---------------------------------------------------------------
	function nlpapp_load_stepthree(){
		nlapp_reset_ui();
		$("tbody","#prior-art-results-table").html("");
        $("tbody","#prior-art-saved-results-table").html("");
		$('#nlpapp-modal-delete-priorartresult').modal('hide');
		$('#nlpapp-modal-delete-savedpriorart').modal('hide');
		$("#nlpapp-filters-notification").html("").hide();
		$("#nlpapp-filters").hide();
		$("#nlpapp_hidefilters").parent().hide();
		$("#nlpapp_showfilters").parent().show();
		nlpapp_load_stepthree_results();
		nlpapp_load_stepthree_savedresults();
	}

	// listeners for pagination clicks
	// ---------------------------------------------------------------
	$( "#pagination_next .btn:not(.disabled)" ).click(function() {
		console.log("pagination next : " + $(this).val() );
		nlpapp_dataobject.current_project.priorart_page = $(this).val();
		nlpapp_load_stepthree_results();
	});
	$( "#pagination_prev .btn:not(.disabled)" ).click(function() {
		console.log("pagination prev : " + $(this).val() );
		nlpapp_dataobject.current_project.priorart_page = $(this).val();
		nlpapp_load_stepthree_results();
	});

	// step three - save manual prior result
	// ---------------------------------------------------------------
	$( "#addsavedpriorart_saved .btn:not(.disabled)" ).click(function() {
		console.log("save manual prior art click");
		validate_addsavedpriorart_saved = nlpapp_validate_form_addsavedpriorart();
		if ( validate_addsavedpriorart_saved === true ){
			console.log("manual prior art pattern is OK");
			var form_data = "result=" + $("#manual_saved_result",".addsavedpriorart_group").val();;
			ajaxCall( nlp_dataroute.step3_save_result_manual , "POST", form_data, nlpapp_load_stepthree_savedresults , ".addsavedpriorart-row",null,"SAVING PRIOR ART...");
		} else {
			console.log("manual prior art is NOT ok:");
		}
	});
	// step three - abstract click, retrieval and display
	// ---------------------------------------------------------------
	$(document.body).on("click", ".nlpapp-priorart-prev", function(){
		if ( !$(this).hasClass("disabled")){
			//nlpapp_show_loader_modal("RETRIEVING ABSTRACT...");
			var abstract_data = $(this).attr("data-target");
			console.log("retrieve abstract" + abstract_data );
			var form_data = "result=" + abstract_data;
			var abstract_end = abstract_data.indexOf(":");
			$(".modal-title","#nlpapp-modal-priorartabstract").text( "ABSTRACT // " + abstract_data.substring(0,abstract_end) );
			ajaxCall( nlp_dataroute.get_abstract , "POST", form_data, nlpapp_showabstract , "","application",null,"RETRIEVING ABSTRACT...");
		}
	});
	function nlpapp_showabstract(data){
		console.log("abstract loaded");
		$(".modal-title","#nlpapp-modal-priorartabstract").text();
		$(".modal-body","#nlpapp-modal-priorartabstract").html("<p>"+ data.abstract +"</p><br><br>");
		nlpapp_hide_loader_modal();
		$('#nlpapp-modal-priorartabstract').modal('show');
	}


	// ---------------------------------------------------------------
	// step three - prior art results load (left side)
	// ---------------------------------------------------------------
	function nlpapp_load_stepthree_results(relay){
		
		$("#nlpapp_stepthree_pagination_row").hide();
		$(".filters-pagination-label").hide();
		$("tbody","#prior-art-results-table").html("");
		$('#nlpapp-modal-delete-priorartresult').modal('hide');
		var form_data = "";
		if ( nlpapp_dataobject.current_project.priorart_page == ""){
			form_data = "page=1";
		} else {
			form_data = "page=" + nlpapp_dataobject.current_project.priorart_page;
		}
		// if relay == relay_true it means this call came from a save/delete/remote function, so we show a different message,
		// otherwise its the default message
		if (relay && relay == "relay_true"){
			ajaxCall( nlp_dataroute.step3_results_load, "POST", form_data, nlpapp_load_stepthree_results_complete, "application", null, "PROCESSING...");
		} else {
			ajaxCall( nlp_dataroute.step3_results_load, "POST", form_data, nlpapp_load_stepthree_results_complete, "application", null, "RETRIEVING PRIOR ART...");
		}
	}
	function nlpapp_load_stepthree_results_complete(data,callback){
		$(".form-feedback,.help-block").removeClass("SUCCESS FIELDLEVEL_ERROR ERROR EXISTS FAIL DENIED MISSING PAYMENT_ERROR").text("").hide();
		// $("#nlpapp-update-results-holder").show();
		// $("#nlpapp-clearupdated-results-holder").show();
		$("#nlpapp-update-results-holder").css("display","table-cell");
		$("#nlpapp-clearupdated-results-holder").css("display","table-cell");
		$("#prior-art-results-table-title").text("Top Results");
		$("#prior-art-results-table").removeClass("filtered-results");
		if(data.prior_art_results == null && data.heading == "NO RESULTS"){
		    $("tbody","#prior-art-results-table").html("<tr class='empty-row-message' style='display:table-row;'><td colspan='4' align='center'><br>You must complete the previous step.<br><br></td></tr>");
		} else {
		    $("tbody","#prior-art-results-table").html("<tr class='empty-row-message' style='display:table-row;'><td colspan='4' align='center'><br>There are no results to display.<br><br></td></tr>");
		}

		// handle pagination logic & presentation
		// ---------------------------------------------------------------
		$(".pagination-label").text(data.label);
		if (data.more == "true" || data.more ){
			// we have more results to show
			$("#pagination_next, #pagination_next .btn").removeClass("disabled");
			$("#pagination_next .btn").removeAttr("disabled");
			$("#pagination_next .btn").val( parseInt(data.page) + 1);
		} else {
			$("#pagination_next, #pagination_next .btn").addClass("disabled");
			$("#pagination_next .btn").attr("disabled", true);
		}
		// check state of previous button
		if ( data.page=="1" || data.page==1){
			$("#pagination_prev, #pagination_prev .btn").addClass("disabled");
			$("#pagination_prev .btn").attr("disabled", true);
		} else {
			$("#pagination_prev .btn").val( parseInt(data.page) - 1);
			$("#pagination_prev, #pagination_prev .btn").removeClass("disabled");
			$("#pagination_prev .btn").removeAttr("disabled");
		}
		
		$("#nlpapp-filters-form").html("");
		if ( data.filters ){
    		// key elements
    		var filter_key_elements = "";
    		//if(data.filters[0].key_elements !== ""){
    			//filter_key_elements= "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by key elements you entered in Step 1, Description.'>?</button></div></div><div class='col-xs-11'><select name='basic[]' multiple='multiple' id='key_elements' name='key_elements' class='form-control 3col active'>";
    			//for(i=0;i<data.filters[0].key_elements.length;i++){
    			//	filter_key_elements = filter_key_elements + "<option value='" + data.filters[0].key_elements[i] + "'>" + data.filters[0].key_elements[i] + "</option>";
    			//}
    			//filter_key_elements = filter_key_elements + "</select></div></div>";
    		//}
    		filter_key_elements= "<div id='nlpapp_stepthree_filters_keyelements_holder'><div class='row filters-row' style='display: flex;align-items: top;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Enter specific words or phrases to look for in the prior art.'>?</button></div></div><div class='col-xs-11'><span id='keyelement-holder'><div class='form-group'><label for=''>Keywords</label><div class='keyelement-row flex-row top'><div class='keyelement-row-field-holder'><input type='text' class='form-control keyelement-field' id='element_1' name='element_1' style='margin-top:.25em;margin-bottom:.25em;'><div class='help-block with-errors'></div></div><div><div class='hex-button-small nlp-orange' id='duplicate-keyelement' style='margin-top:.25em;margin-bottom:.25em;'><button type='button' class='btn btn-primary'><div class='icon nlpapp-icon-plus'></div></button></div></div></div></div></span></div></div></div>";

    		// result elements
    		var filter_result_elements = "";
    		if(data.filters[1].result_elements !== ""){
    			filter_result_elements= "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by words or phrases that appear most frequently in the search results.'>?</button></div></div><div class='col-xs-11' style='margin-top:.25em;'><select name='basic[]' multiple='multiple' id='result_elements' name='result_elements' class='form-control 3col active'>";
    			for(i=0;i<data.filters[1].result_elements.length;i++){
    				filter_result_elements = filter_result_elements + "<option value='" + data.filters[1].result_elements[i] + "'>" + data.filters[1].result_elements[i] + "</option>";
    			}
    			filter_result_elements = filter_result_elements + "</select></div></div>";
    		}

    		// cpc elements
    		var filter_cpc_subclasses = "";
    		if(data.filters[2].cpc_subclasses !== ""){
    			filter_cpc_subclasses= "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by CPC subclasses you selected.'>?</button></div></div><div class='col-xs-11'><select name='basic[]' multiple='multiple' id='cpc_subclasses' name='cpc_subclasses' class='form-control 3col active'>";
    			for(i=0;i<data.filters[2].cpc_subclasses.length;i++){
    				filter_cpc_subclasses = filter_cpc_subclasses + "<option value='" + data.filters[2].cpc_subclasses[i] + "'>" + data.filters[2].cpc_subclasses[i] + "</option>";
    			}
    			filter_cpc_subclasses = filter_cpc_subclasses + "</select></div></div>";
    		}

			// applicant names
    		var filter_applicant_names = "";
    		if(data.filters[3].applicants !== ""){
    			filter_applicant_names= "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by name of the original applicant.'>?</button></div></div><div class='col-xs-11' style='margin-top:.25em;'><select name='basic[]' multiple='multiple' id='applicant_names' name='applicant_names' class='form-control 3col active'>";
    			for(i=0;i<data.filters[3].applicants.length;i++){
    				filter_applicant_names = filter_applicant_names + "<option value='" + data.filters[3].applicants[i] + "'>" + data.filters[3].applicants[i] + "</option>";
    			}
    			filter_applicant_names = filter_applicant_names + "</select></div></div>";
    		}

    		// embed date select
    		var filter_dates = "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by publication date of the search results. YYYY-MM-DD.'>?</button></div></div><div class='col-xs-11'><div class='form-group' style='width:49%;float:left;margin-right:1%;margin-bottom:0;'><label for='nlpapp-filters-fromdate'>From </label><div style='position:relative;'><div class='icon nlpapp-icon-calendar nlpapp-datepicker-icon'></div><input type='text' class='form-control' id='nlpapp-filters-fromdate' value='' style='background:#fff !important;margin-top:0;'></div></div><div class='form-group' style='width:49%;float:left;margin-left:1%;margin-bottom:0;'><label for=''nlpapp-filters-todate'>To </label><div style='position:relative;'><div class='icon nlpapp-icon-calendar nlpapp-datepicker-icon'></div><input type='text' class='form-control' id='nlpapp-filters-todate' value='' style='background:#fff !important;margin-top:0;'></div></div></div></div>";
    		// apply multiselect scripts to filter dropdowns
    		// **** we may need to destroy these
    		$("#nlpapp-filters-form").prepend("<div class='form-feedback'></div>").prepend(filter_dates).prepend(filter_applicant_names).prepend(filter_cpc_subclasses).prepend(filter_result_elements).prepend(filter_key_elements);
    		//if ( filter_key_elements !== ""){
    			//$("#key_elements","#nlpapp-filters-form").multiselect({columns: 2,placeholder: "By Key Elements",search: false,selectAll: false});
    		//}
			if ( filter_result_elements !== ""){
    			$("#result_elements","#nlpapp-filters-form").multiselect({columns: 2,placeholder: "Suggested Keywords",search: false,selectAll: false});
    		}
    		if ( filter_cpc_subclasses !== ""){
    			$("#cpc_subclasses","#nlpapp-filters-form").multiselect({columns: 2,placeholder: "CPC Subclasses",search: false,selectAll: false});
    		}
			if ( filter_applicant_names !== ""){
    			$("#applicant_names","#nlpapp-filters-form").multiselect({columns: 2,placeholder: "Applicants",search: false,selectAll: false});
    		}
            $("#nlpapp-filters-fromdate").datepicker({
                onClose: function(selectedDate){
                    $("#nlpapp-filters-todate","#nlpapp-filters-form").datepicker("option","minDate",selectedDate);
                }
            });
            $("#nlpapp-filters-todate").datepicker({
                onClose: function(selectedDate){
                    $("#nlpapp-filters-fromdate","#nlpapp-filters-form").datepicker("option","maxDate",selectedDate);
                }
            });
            $("#nlpapp-filters-fromdate","#nlpapp-filters-form").datepicker("option","dateFormat","yy-mm-dd");
            $("#nlpapp-filters-todate","#nlpapp-filters-form").datepicker("option","dateFormat","yy-mm-dd");
		}
		if(data.prior_art_results){
			for(i=0;i<data.prior_art_results.length;i++){
				var disabled_flag = "";
				if( data.prior_art_results[i].s ){
					disabled_flag = " disabled";
				}
				// changes results
				var changedresult = "";
				if (data.prior_art_results[i].x){
					var change = 0;
					change = parseInt( data.prior_art_results[i].x );
					console.log("change is " + change);
					if ( change > 0 ){
						changedresult = "<br><div style='display:inline;'><img src='/static/images/filters_change_up.png' style='margin-bottom:3px;'>&nbsp;<span style='color:#888;'>"+ change + "</span></div>";
					} else if ( change < 0 ){
						changedresult = "<br><div style='display:inline;'><img src='/static/images/filters_change_down.png' style='margin-bottom:3px;'>&nbsp;<span style='color:#888;'>"+ Math.abs(change) + "</span></div>";
					}
				}
				$("tbody","#prior-art-results-table").append("<tr data-id='" + data.prior_art_results[i].p + "' data-text='" + data.prior_art_results[i].T + "' data-cpc='" + data.prior_art_results[i].c + "'><td width='66px' scope='row'><button type='button' class='nlpapp-button nlpapp-priorart-delete"+disabled_flag+"'><div class='icon nlpapp-icon-delete'></div></button><button type='button' class='nlpapp-button nlpapp-priorart-save"+disabled_flag+"'><div class='icon nlpapp-icon-plus'></div></button><br><button type='button' class='nlpapp-button nlpapp-priorart-prev' data-target='" + data.prior_art_results[i].p +":" + data.prior_art_results[i].c + "'><div class='icon nlpapp-icon-magnify'></div></button><a href='https://www.patentbots.com/patentplex/" + data.prior_art_results[i].p + "' target='_blank'><button type='button' class='nlpapp-button nlpapp-priorart-patentbots'><div class='icon nlpapp-icon-patentbots'></div></button></a></td><td width='50px'><a href='https://patents.google.com/patent/" + data.prior_art_results[i].p + "' target='_blank'>" + data.prior_art_results[i].p + "</a>" + changedresult + "</td><td width='*'  valign='middle'>" + data.prior_art_results[i].t + "</td><td width='50px' align='right' valign='middle'><var>" + data.prior_art_results[i].c + "</var></td></tr>");
			}
		}
		//
		if(data.prior_art_results == null && data.heading == "NO RESULTS"){
		    $("#nlpapp_stepthree_filters_widget_row").hide();
			$("#nlpapp_stepthree_pagination_row").hide();
			$("#nlpapp-update-results-holder").hide();
			$("#nlpapp-clearupdated-results-holder").hide();
			
		} else {
			console.log("hide buttons");
		    $("#nlpapp_stepthree_filters_widget_row").show();
			$("#nlpapp_stepthree_pagination_row").show();
			$("#nlpapp-update-results-holder").show();
			$("#nlpapp-clearupdated-results-holder").show();
		}
		//
		if(data.heading){
			$("#prior-art-results-table-title").text(data.heading);
		}
		if(data.heading == "NO RESULTS"){
		    console.log("no results!");
			$("#prior-art-results-table-title").text("NO RESULTS");
		}
		check_priorart_table("prior-art-results-table");
		nlpapp_hide_loader_modal();
	}
	function nlpapp_load_stepthree_results_filtered(relay){
		$('#nlpapp-modal-delete-priorartresult').modal('hide');
		// if relay == relay_true it means this call came from a save/delete/remote function, so we show a different message,
		// otherwise its the default message
		if(relay && relay == "relay_true"){
			ajaxCall( nlp_dataroute.step3_results_load, "POST", "filtered=1", nlpapp_load_stepthree_results_filtered_complete, "application", null, "PROCESSING...");
		} else {
			ajaxCall( nlp_dataroute.step3_results_load, "POST", "filtered=1", nlpapp_load_stepthree_results_filtered_complete, "application", null, "RETRIEVING PRIOR ART...");
		}

	}
	function nlpapp_load_stepthree_results_filtered_complete(data,callback){
		$(".form-feedback,.help-block").removeClass("SUCCESS FIELDLEVEL_ERROR ERROR EXISTS FAIL DENIED MISSING PAYMENT_ERROR").text("").hide();
		$("#nlpapp-update-results-holder").show();
		$("#nlpapp-clearupdated-results-holder").show();
		console.log("hiding pagination");
		$("#nlpapp_stepthree_pagination_row").hide();
		$(".filters-pagination-label").hide();
		$("#nlpapp-update-results-holder").css("display","table-cell");
		$("#nlpapp-clearupdated-results-holder").css("display","table-cell");
		$("#prior-art-results-table-title").text("Filtered Results");
		if(data.prior_art_results == null && data.heading == "NO RESULTS"){
		    $("tbody","#prior-art-results-table").html("<tr class='empty-row-message' style='display:table-row;'><td colspan='4' align='center'><br>You must complete the previous step.<br><br></td></tr>");
			$("#nlpapp-update-results-holder").hide();
			$("#nlpapp-clearupdated-results-holder").hide();
		} else {
		    $("tbody","#prior-art-results-table").html("<tr class='empty-row-message' style='display:table-row;'><td colspan='4' align='center'><br>There are no results to display.<br><br></td></tr>");
			$("#nlpapp-update-results-holder").hide();
			$("#nlpapp-clearupdated-results-holder").hide();
		}
		if(data.prior_art_results){
			for(i=0;i<data.prior_art_results.length;i++){
				var disabled_flag = "";
				if( data.prior_art_results[i].s ){
					disabled_flag = " disabled";
				}
				// changes results
				var changedresult = "";
				if (data.prior_art_results[i].x){
					var change = 0;
					change = parseInt( data.prior_art_results[i].x );
					console.log("change is " + change);
					if ( change > 0 ){
						changedresult = "<br><div style='display:inline;'><img src='/static/images/filters_change_up.png' style='margin-bottom:3px;'>&nbsp;<span style='color:#888;'>"+ change + "</span></div>";
					} else if ( change < 0 ){
						changedresult = "<br><div style='display:inline;'><img src='/static/images/filters_change_down.png' style='margin-bottom:3px;'>&nbsp;<span style='color:#888;'>"+ Math.abs(change) + "</span></div>";
					}
				}
				$("#prior-art-results-table").addClass("filtered-results");
				$("tbody","#prior-art-results-table").append("<tr data-id='" + data.prior_art_results[i].p + "' data-text='" + data.prior_art_results[i].T + "' data-cpc='" + data.prior_art_results[i].c + "'><td width='66px' scope='row'><button type='button' class='nlpapp-button nlpapp-priorart-delete"+disabled_flag+"'><div class='icon nlpapp-icon-delete'></div></button><button type='button' class='nlpapp-button nlpapp-priorart-save"+disabled_flag+"'><div class='icon nlpapp-icon-plus'></div></button><br><button type='button' class='nlpapp-button nlpapp-priorart-prev' data-target='" + data.prior_art_results[i].p +":" + data.prior_art_results[i].c + "'><div class='icon nlpapp-icon-magnify'></div></button><a href='https://www.patentbots.com/patentplex/" + data.prior_art_results[i].p + "' target='_blank'><button type='button' class='nlpapp-button nlpapp-priorart-patentbots'><div class='icon nlpapp-icon-patentbots'></div></button></a></td><td width='100px'><a href='https://patents.google.com/patent/" + data.prior_art_results[i].p + "' target='_blank'>" + data.prior_art_results[i].p + "</a>" + changedresult + "</td><td width='*'  valign='middle'>" + data.prior_art_results[i].t + "</td><td width='50px' align='right' valign='middle'><var>" + data.prior_art_results[i].c + "</var></td></tr>");
				// show filtered info
				var key_elements_filter = "";
				var result_elements_filter = "";
				var date_filter = "";
				var applicants_filter = "";
				var filter_notification_array = [];
				// key element
				if ( data.prior_art_results[i].k ){
					key_elements_filter = "Keywords :";
					for(x=0;x<data.prior_art_results[i].k.length;x++){
						key_elements_filter = key_elements_filter + " <span class='data'>" + data.prior_art_results[i].k[x] + "</span>,";
					}
					key_elements_filter = key_elements_filter.slice(0, -1); // remove trailing ','
					filter_notification_array.push(key_elements_filter);
				}
				// result elements
				if ( data.prior_art_results[i].r ){
					result_elements_filter = "Suggested Keywords :";
					for(x=0;x<data.prior_art_results[i].r.length;x++){
						result_elements_filter = result_elements_filter + " <span class='data'>" + data.prior_art_results[i].r[x] + "</span>,";
					}
					result_elements_filter = result_elements_filter.slice(0, -1); // remove trailing ','
					filter_notification_array.push(result_elements_filter);
				}
				// date
				if ( data.prior_art_results[i].d ){
					date_filter = "Date : <span class='data'>" + data.prior_art_results[i].d +"</span>";
					filter_notification_array.push(date_filter);
				}
				// applicants
				if ( data.prior_art_results[i].a ){
					applicants_filter = "Applicants : <span class='data'>" + data.prior_art_results[i].a +"</span>";
					filter_notification_array.push(applicants_filter);
				}
				filter_notification_text = filter_notification_array.join("<br>");
				$("tbody","#prior-art-results-table").append("<tr class='filtered-notification'><td scope='row'></td><td colspan='3'>" + filter_notification_text + "</td></tr>");
			}
		}
		//
		if(data.prior_art_results == null && data.heading == "NO RESULTS"){
		    $("#nlpapp_stepthree_filters_widget_row").hide();
		} else {
		    $("#nlpapp_stepthree_filters_widget_row").show();
		}
		//
		$("#prior-art-results-table-title").text("Filtered Results");
		check_priorart_table("prior-art-results-table");
		nlpapp_hide_loader_modal();
	}
	$( "#nlpapp_step_three_form" ).submit(function(event) {
		event.preventDefault();
		ajaxCall( nlp_dataroute.step3_submit , "POST", "", nlpapp_submit_stepthree_complete, "#nlpapp_step_three_form",null,"PREDICTING OUTCOME...");
	});
	function nlpapp_submit_stepthree_complete(data){
		nlpapp_set_progress_tabs(4);
		nlp_router.navigate("#step4");
	}
	// ---------------------------------------------------------------
	// step three - prior art results load filtered (left side)
	// ---------------------------------------------------------------
	function nlpapp_load_stepthree_filtered_results(form_data){
		ajaxCall( nlp_dataroute.apply_filters_submit, "POST", form_data, nlpapp_load_stepthree_filtered_results_complete, "#nlpapp-filters-form",null,"APPLYING FILTERS...");
	}
	function nlpapp_load_stepthree_filtered_results_complete(data,callback){
		$(".form-feedback,.help-block").removeClass("SUCCESS FIELDLEVEL_ERROR ERROR EXISTS FAIL DENIED MISSING PAYMENT_ERROR").text("").hide();
	    console.log("back");
		$(".help-block,.form-feedback","#container-step3").text("");
		console.log("hiding pagination");
		$("#nlpapp_stepthree_pagination_row").hide();
		$(".filters-pagination-label").hide();
		$("#nlpapp-update-results-holder").show();
		$("#nlpapp-clearupdated-results-holder").show();
		$("#nlpapp-update-results-holder").css("display","table-cell");
		$("#nlpapp-clearupdated-results-holder").css("display","table-cell");
		if(data.prior_art_results == null && data.heading == "NO RESULTS"){
		    $("tbody","#prior-art-results-table").html("<tr class='empty-row-message' style='display:table-row;'><td colspan='4' align='center'><br>You must complete the previous step.<br><br></td></tr>");
			$("#nlpapp-update-results-holder").hide();
			$("#nlpapp-clearupdated-results-holder").hide();
		} else {
		    $("tbody","#prior-art-results-table").html("<tr class='empty-row-message' style='display:table-row;'><td colspan='4' align='center'><br>There are no results to display.<br><br></td></tr>");
			$("#nlpapp-update-results-holder").hide();
			$("#nlpapp-clearupdated-results-holder").hide();
		}
		if(data.label){
			$(".filters-pagination-label").text(data.label).show();
			console.log(data.label);
		}
		if(data.prior_art_results){
			for(i=0;i<data.prior_art_results.length;i++){
				var disabled_flag = "";
				if( data.prior_art_results[i].s ){
					disabled_flag = " disabled";
				}
				// changes results
				var changedresult = "";
				if (data.prior_art_results[i].x){
					var change = 0;
					change = parseInt( data.prior_art_results[i].x );
					console.log("change is " + change);
					if ( change > 0 ){
						changedresult = "<br><div style='display:inline;'><img src='/static/images/filters_change_up.png' style='margin-bottom:3px;'>&nbsp;<span style='color:#888;'>"+ change + "</span></div>";
					} else if ( change < 0 ){
						changedresult = "<br><div style='display:inline;'><img src='/static/images/filters_change_down.png' style='margin-bottom:3px;'>&nbsp;<span style='color:#888;'>"+ Math.abs(change) + "</span></div>";
					}
				}
				$("#prior-art-results-table").addClass("filtered-results");
				$("tbody","#prior-art-results-table").append("<tr data-id='" + data.prior_art_results[i].p + "' data-text='" + data.prior_art_results[i].T + "' data-cpc='" + data.prior_art_results[i].c + "'><td width='66px' scope='row'><button type='button' class='nlpapp-button nlpapp-priorart-delete"+disabled_flag+"'><div class='icon nlpapp-icon-delete'></div></button><button type='button' class='nlpapp-button nlpapp-priorart-save"+disabled_flag+"'><div class='icon nlpapp-icon-plus'></div></button><br><button type='button' class='nlpapp-button nlpapp-priorart-prev' data-target='" + data.prior_art_results[i].p +":" + data.prior_art_results[i].c + "'><div class='icon nlpapp-icon-magnify'></div></button><a href='https://www.patentbots.com/patentplex/" + data.prior_art_results[i].p + "' target='_blank'><button type='button' class='nlpapp-button nlpapp-priorart-patentbots'><div class='icon nlpapp-icon-patentbots'></div></button></a></td><td width='100px'><a href='https://patents.google.com/patent/" + data.prior_art_results[i].p + "' target='_blank'>" + data.prior_art_results[i].p + "</a>" + changedresult + "</td><td width='*'  valign='middle'>" + data.prior_art_results[i].t + "</td><td width='50px' align='right' valign='middle'><var>" + data.prior_art_results[i].c + "</var></td></tr>");
				// show filtered info
				var key_elements_filter = "";
				var result_elements_filter = "";
				var date_filter = "";
				var applicants_filter = "";
				var filter_notification_array = [];
				// key element
				if ( data.prior_art_results[i].k){
					key_elements_filter = "Keywords :";
					for(x=0;x<data.prior_art_results[i].k.length;x++){
						key_elements_filter = key_elements_filter + " <span class='data'>" + data.prior_art_results[i].k[x] + "</span>,";
					}
					key_elements_filter = key_elements_filter.slice(0, -1); // remove trailing ','
					filter_notification_array.push(key_elements_filter);
				}
				// result elements
				if ( data.prior_art_results[i].r){
					result_elements_filter = "Suggested Keywords :";
					for(x=0;x<data.prior_art_results[i].r.length;x++){
						result_elements_filter = result_elements_filter + " <span class='data'>" + data.prior_art_results[i].r[x] + "</span>,";
					}
					result_elements_filter = result_elements_filter.slice(0, -1); // remove trailing ','
					filter_notification_array.push(result_elements_filter);
				}
				// date
				if ( data.prior_art_results[i].d){
					date_filter = "Date : <span class='data'>" + data.prior_art_results[i].d +"</span>";
					filter_notification_array.push(date_filter);
				}
				// applicants
				if ( data.prior_art_results[i].a ){
					applicants_filter = "Applicants : <span class='data'>" + data.prior_art_results[i].a +"</span>";
					filter_notification_array.push(applicants_filter);
				}
				filter_notification_text = filter_notification_array.join("<br>");
				$("tbody","#prior-art-results-table").append("<tr class='filtered-notification'><td scope='row'></td><td colspan='3'>" + filter_notification_text + "</td></tr>");
			}
		}
		//
		if(data.prior_art_results == null && data.heading == "NO RESULTS"){
		    $("#nlpapp_stepthree_filters_widget_row").hide();
		} else {
		    $("#nlpapp_stepthree_filters_widget_row").show();
		}
		//
		$("#prior-art-results-table-title").text("Filtered Results");
		check_priorart_table("prior-art-results-table");
		nlpapp_hide_loader_modal();
	}
	// ---------------------------------------------------------------
	// step three - update prior art results
	// ---------------------------------------------------------------
	function nlpapp_load_stepthree_updated_results(form_data){
		ajaxCall( nlp_dataroute.update_results_submit , "POST", form_data, nlpapp_load_stepthree_updated_results_complete, "#nlpapp-update-results-holder", null, "UPDATING RESULTS...");
	}
	function nlpapp_load_stepthree_updated_results_complete(data,callback){
		nlpapp_dataobject.current_project.priorart_page = 1;
		//tepthree_filters_clear();
		nlpapp_load_stepthree_results();
	}
	function nlpapp_load_stepthree_updated_results_completeold(data,callback){
		$(".form-feedback,.help-block").removeClass("SUCCESS FIELDLEVEL_ERROR ERROR EXISTS FAIL DENIED MISSING PAYMENT_ERROR").text("").hide();
		stepthree_filters_clear();
		$("#nlpapp-update-results-holder").show();
		$("#nlpapp-clearupdated-results-holder").show();
		$("#nlpapp-update-results-holder").css("display","table-cell");
		$("#nlpapp-clearupdated-results-holder").css("display","table-cell");
		$("tbody","#prior-art-results-table").html("<tr class='empty-row-message' style='display:table-row;'><td colspan='4' align='center'><br>There are no more results after updating.<br><br></td></tr>");

		$("#nlpapp-filters-form").html("");
		if ( data.filters ){
    		// key elements
    		var filter_key_elements = "";
    		//if(data.filters[0].key_elements !== ""){
    			//filter_key_elements= "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by key elements you entered in Step 1, Description.'>?</button></div></div><div class='col-xs-11'><select name='basic[]' multiple='multiple' id='key_elements' name='key_elements' class='form-control 3col active'>";
    			//for(i=0;i<data.filters[0].key_elements.length;i++){
    			//	filter_key_elements = filter_key_elements + "<option value='" + data.filters[0].key_elements[i] + "'>" + data.filters[0].key_elements[i] + "</option>";
    			//}
    			//filter_key_elements = filter_key_elements + "</select></div></div>";
    		//}
    		filter_key_elements= "<div id='nlpapp_stepthree_filters_keyelements_holder'><div class='row filters-row' style='display: flex;align-items: top;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Enter specific words or phrases to look for in the prior art.'>?</button></div></div><div class='col-xs-11'><span id='keyelement-holder'><div class='form-group'><label for=''>Keywords</label><div class='keyelement-row flex-row top'><div class='keyelement-row-field-holder'><input type='text' class='form-control keyelement-field' id='element_1' name='element_1' style='margin-top:.25em;margin-bottom:.25em;'><div class='help-block with-errors'></div></div><div><div class='hex-button-small nlp-orange' id='duplicate-keyelement' style='margin-top:.25em;margin-bottom:.25em;'><button type='button' class='btn btn-primary'><div class='icon nlpapp-icon-plus'></div></button></div></div></div></div></span></div></div></div>";

    		// result elements
    		var filter_result_elements = "";
    		if(data.filters[1].result_elements !== ""){
    			filter_result_elements= "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by words or phrases that commonly appear in the search results.'>?</button></div></div><div class='col-xs-11' style='margin-top:.25em;'><select name='basic[]' multiple='multiple' id='result_elements' name='result_elements' class='form-control 3col active'>";
    			for(i=0;i<data.filters[1].result_elements.length;i++){
    				filter_result_elements = filter_result_elements + "<option value='" + data.filters[1].result_elements[i] + "'>" + data.filters[1].result_elements[i] + "</option>";
    			}
    			filter_result_elements = filter_result_elements + "</select></div></div>";
    		}

    		// cpc elements
    		var filter_cpc_subclasses = "";
    		if(data.filters[2].cpc_subclasses !== ""){
    			filter_cpc_subclasses= "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by CPC subclasses you selected.'>?</button></div></div><div class='col-xs-11'><select name='basic[]' multiple='multiple' id='cpc_subclasses' name='cpc_subclasses' class='form-control 3col active'>";
    			for(i=0;i<data.filters[2].cpc_subclasses.length;i++){
    				filter_cpc_subclasses = filter_cpc_subclasses + "<option value='" + data.filters[2].cpc_subclasses[i] + "'>" + data.filters[2].cpc_subclasses[i] + "</option>";
    			}
    			filter_cpc_subclasses = filter_cpc_subclasses + "</select></div></div>";
    		}

			// applicant names
    		var filter_applicant_names = "";
    		if(data.filters[3].applicants !== ""){
    			filter_applicant_names= "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by name of the original applicant.'>?</button></div></div><div class='col-xs-11' style='margin-top:.25em;'><select name='basic[]' multiple='multiple' id='applicant_names' name='applicant_names' class='form-control 3col active'>";
    			for(i=0;i<data.filters[3].applicants.length;i++){
					filter_applicant_names = filter_applicant_names + "<option value='" + data.filters[3].applicants[i] + "'>" + data.filters[3].applicants[i] + "</option>";
    			}
    			filter_applicant_names = filter_applicant_names + "</select></div></div>";
    		}

    		// embed date select
    		var filter_dates = "<div class='row filters-row' style='display: flex;align-items: center;'><div class='col-xs-1'><div class='hex-button-helper'><button type='button' class='btn btn-primary' data-toggle='tooltip' data-placement='top' title='Sort by publication date of the search results. YYYY-MM-DD.'>?</button></div></div><div class='col-xs-11'><div class='form-group' style='width:49%;float:left;margin-right:1%;margin-bottom:0;'><label for='nlpapp-filters-fromdate'>From </label><div style='position:relative;'><div class='icon nlpapp-icon-calendar nlpapp-datepicker-icon'></div><input type='text' class='form-control' id='nlpapp-filters-fromdate' value='' style='background:#fff !important;margin-top:0;'></div></div><div class='form-group' style='width:49%;float:left;margin-left:1%;margin-bottom:0;'><label for=''nlpapp-filters-todate'>To </label><div style='position:relative;'><div class='icon nlpapp-icon-calendar nlpapp-datepicker-icon'></div><input type='text' class='form-control' id='nlpapp-filters-todate' value='' style='background:#fff !important;margin-top:0;'></div></div></div></div>";
    		// apply multiselect scripts to filter dropdowns
    		// **** we may need to destroy these
    		$("#nlpapp-filters-form").prepend("<div class='form-feedback'></div>").prepend(filter_dates).prepend(filter_applicant_names).prepend(filter_cpc_subclasses).prepend(filter_result_elements).prepend(filter_key_elements);
    		//if ( filter_key_elements !== ""){
    			//$("#key_elements","#nlpapp-filters-form").multiselect({columns: 2,placeholder: "By Key Elements",search: false,selectAll: false});
    		//}
    		if ( filter_result_elements !== ""){
    			$("#result_elements","#nlpapp-filters-form").multiselect({columns: 2,placeholder: "Suggested Keywords",search: false,selectAll: false});
    		}
    		if ( filter_cpc_subclasses !== ""){
    			$("#cpc_subclasses","#nlpapp-filters-form").multiselect({columns: 2,placeholder: "CPC Subclasses",search: false,selectAll: false});
    		}
			if ( filter_applicant_names !== ""){
    			$("#applicant_names","#nlpapp-filters-form").multiselect({columns: 2,placeholder: "Applicants",search: false,selectAll: false});
    		}
            $("#nlpapp-filters-fromdate").datepicker({
                onClose: function(selectedDate){
                    $("#nlpapp-filters-todate","#nlpapp-filters-form").datepicker("option","minDate",selectedDate);
                }
            });
            $("#nlpapp-filters-todate").datepicker({
                onClose: function(selectedDate){
                    $("#nlpapp-filters-fromdate","#nlpapp-filters-form").datepicker("option","maxDate",selectedDate);
                }
            });
            $("#nlpapp-filters-fromdate","#nlpapp-filters-form").datepicker("option","dateFormat","yy-mm-dd");
            $("#nlpapp-filters-todate","#nlpapp-filters-form").datepicker("option","dateFormat","yy-mm-dd");
		}

		if(data.prior_art_results){
			for(i=0;i<data.prior_art_results.length;i++){
				var disabled_flag = "";
				if( data.prior_art_results[i].s ){
					disabled_flag = " disabled";
				}
				// changes results
				var changedresult = "";
				if (data.prior_art_results[i].x){
					var change = 0;
					change = parseInt( data.prior_art_results[i].x );
					console.log("change is " + change);
					if ( change > 0 ){
						changedresult = "<br><div style='display:inline;'><img src='/static/images/filters_change_up.png' style='margin-bottom:3px;'>&nbsp;<span style='color:#888;'>"+ change + "</span></div>";
					} else if ( change < 0 ){
						changedresult = "<br><div style='display:inline;'><img src='/static/images/filters_change_down.png' style='margin-bottom:3px;'>&nbsp;<span style='color:#888;'>"+ Math.abs(change) + "</span></div>";
					}
				}
				//$("#prior-art-results-table").addClass("filtered-results");
				$("tbody","#prior-art-results-table").append("<tr data-id='" + data.prior_art_results[i].p + "' data-text='" + data.prior_art_results[i].T + "' data-cpc='" + data.prior_art_results[i].c + "'><td width='66px' scope='row'><button type='button' class='nlpapp-button nlpapp-priorart-delete"+disabled_flag+"'><div class='icon nlpapp-icon-delete'></div></button><button type='button' class='nlpapp-button nlpapp-priorart-save"+disabled_flag+"'><div class='icon nlpapp-icon-plus'></div></button><br><button type='button' class='nlpapp-button nlpapp-priorart-prev' data-target='" + data.prior_art_results[i].p +":" + data.prior_art_results[i].c + "'><div class='icon nlpapp-icon-magnify'></div></button><a href='https://www.patentbots.com/patentplex/" + data.prior_art_results[i].p + "' target='_blank'><button type='button' class='nlpapp-button nlpapp-priorart-patentbots'><div class='icon nlpapp-icon-patentbots'></div></button></a></td><td width='100px'><a href='https://patents.google.com/patent/" + data.prior_art_results[i].p + "' target='_blank'>" + data.prior_art_results[i].p + "</a>" + changedresult + "</td><td width='*'  valign='middle'>" + data.prior_art_results[i].t + "</td><td width='50px' align='right' valign='middle'><var>" + data.prior_art_results[i].c + "</var></td></tr>");
				// // show filtered info
				// var key_elements_filter = "";
				// var result_elements_filter = "";
				// var date_filter = "";
				// var applicants_filter = "";
				// var filter_notification_array = [];
				// // key element
				// if ( data.prior_art_results[i].k){
				// 	key_elements_filter = "Keywords :";
				// 	for(x=0;x<data.prior_art_results[i].k.length;x++){
				// 		key_elements_filter = key_elements_filter + " <span class='data'>" + data.prior_art_results[i].k[x] + "</span>,";
				// 	}
				// 	key_elements_filter = key_elements_filter.slice(0, -1); // remove trailing ','
				// 	filter_notification_array.push(key_elements_filter);
				// }
				// // result elements
				// if ( data.prior_art_results[i].r){
				// 	result_elements_filter = "Suggested Keywords :";
				// 	for(x=0;x<data.prior_art_results[i].r.length;x++){
				// 		result_elements_filter = result_elements_filter + " <span class='data'>" + data.prior_art_results[i].r[x] + "</span>,";
				// 	}
				// 	result_elements_filter = result_elements_filter.slice(0, -1); // remove trailing ','
				// 	filter_notification_array.push(result_elements_filter);
				// }
				// // date
				// if ( data.prior_art_results[i].d){
				// 	date_filter = "Date : <span class='data'>" + data.prior_art_results[i].d +"</span>";
				// 	filter_notification_array.push(date_filter);
				// }
				// // applicants
				// if ( data.prior_art_results[i].a ){
				// 	applicants_filter = "Applicants : <span class='data'>" + data.prior_art_results[i].a +"</span>";
				// 	filter_notification_array.push(applicants_filter);
				// }
				// filter_notification_text = filter_notification_array.join("<br>");
				// //$("tbody","#prior-art-results-table").append("<tr class='filtered-notification'><td scope='row'></td><td colspan='3'>" + filter_notification_text + "</td></tr>");
			}
		}
		//
		if(data.prior_art_results == null && data.heading == "NO RESULTS"){
		    $("#nlpapp_stepthree_filters_widget_row").hide();
		} else {
		    $("#nlpapp_stepthree_filters_widget_row").show();
		}
		//
		$("#prior-art-results-table-title").text("Updated Results");
		check_priorart_table("prior-art-results-table");
		nlpapp_hide_loader_modal();
	}
	// ---------------------------------------------------------------
	// step three - clear updated prior art results
	// ---------------------------------------------------------------
	function nlpapp_load_stepthree_clearupdated_results(){
		ajaxCall( nlp_dataroute.clearupdate_results_submit , "POST", "", nlpapp_load_stepthree_clearupdated_results_complete, "#nlpapp-clearupdated-results-holder", null, "RETRIEVING PRIOR ART...");

	}
	function nlpapp_load_stepthree_clearupdated_results_complete(data,callback){
		$(".form-feedback,.help-block").removeClass("SUCCESS FIELDLEVEL_ERROR ERROR EXISTS FAIL DENIED MISSING PAYMENT_ERROR").text("").hide();
		console.log("data is ");
		console.log(data);
		nlpapp_dataobject.current_project.priorart_page = data.page;
		console.log(nlpapp_dataobject.current_project.priorart_page);
		stepthree_filters_clear();
		nlpapp_load_stepthree_results();
	}
	// ---------------------------------------------------------------
	// step three - prior art saved results load (right side)
	// ---------------------------------------------------------------
	function nlpapp_load_stepthree_savedresults(relay){
		console.log("nlpapp_load_stepthree_savedresults");
		console.log("disabled download analysis");
		$("#nlpapp-download-analysis-saved").addClass("disabled");
		$("#nlpapp-download-analysis-saved button").attr("disabled", true);
		$('#nlpapp-modal-delete-savedpriorart').modal('hide');
		// if relay == relay_true it means this call came from a save/delete/remote function, so we show a different message,
		// otherwise its the default message
		if ( relay && relay == "relay_true"){
			ajaxCall( nlp_dataroute.step3_savedresults_load, "GET", "", nlpapp_load_stepthree_savedresults_complete, "application", null, "PROCESSING...");
		} else {
			ajaxCall( nlp_dataroute.step3_savedresults_load, "GET", "", nlpapp_load_stepthree_savedresults_complete, "application", null, "RETRIEVING PRIOR ART...");
		}
	}
	function nlpapp_load_stepthree_savedresults_complete(data,callback){
		$(".form-feedback,.help-block").removeClass("SUCCESS FIELDLEVEL_ERROR ERROR EXISTS FAIL DENIED MISSING PAYMENT_ERROR").text("").hide();
		$("#nlpapp-download-analysis").addClass("disabled").attr("disabled", true);
		$("tbody","#prior-art-saved-results-table").html("<tr class='empty-row-message' style='display:table-row;'><td colspan='4' align='center'><br>You have no Saved Prior Art results.<br><br></td></tr>");
		if(data.prior_art_saved){
			for(i=0;i<data.prior_art_saved.length;i++){
				console.log("enable download analysis");
				var disabled_flag = "";
				if( data.prior_art_saved[i].s ){
					disabled_flag = " disabled";
				}
				$("tbody","#prior-art-saved-results-table").append("<tr data-id='" + data.prior_art_saved[i].p + "' data-text='" + data.prior_art_saved[i].T + "' data-cpc='" + data.prior_art_saved[i].c + "'><td height='100%' width='30px' scope='row'><button type='button' class='nlpapp-button nlpapp-priorart-removesaved'><div class='icon nlpapp-icon-minus'></div></button></td><td width='100px'><a href='https://patents.google.com/patent/" + data.prior_art_saved[i].p + "' target='_blank'>" + data.prior_art_saved[i].p + "</a></td><td width='*'  valign='middle'>" + data.prior_art_saved[i].t + "</td><td width='110px' align='right' valign='middle'><var>" + data.prior_art_saved[i].c + "</var></td></tr>");
			}
			$("#nlpapp-download-analysis-saved").removeClass("disabled");
			$("#nlpapp-download-analysis-saved button").removeAttr("disabled");
		}
		check_priorart_table("prior-art-saved-results-table");
		nlpapp_hide_loader_modal();
	}

	// ---------------------------------------------------------------
	// step four load & setup
	// ---------------------------------------------------------------
	function nlpapp_load_stepfour(){
		$(".analysis_holder","#container-step4").html("");
		nlapp_reset_ui();
		$('#nlpapp-modal-delete-priorartresult').modal('hide');
		ajaxCall( nlp_dataroute.step4_load, "GET", "", nlpapp_load_stepfour_complete, "application", null, "PREDICTING OUTCOME...");
	}
	function nlpapp_load_stepfour_complete(data){
	var analysis_html = "";
    	if( data.high_tech == null && data.life_sciences == null){
    		// low risk for both high_tech and life_sciences
    		analysis_html = analysis_html + "<div class='analysis-result low'><div class='row'><div class='col-xs-9'><b>Likelihood of a s. 101 rejection by the USPTO</b><br><br></div><div class='col-xs-3'></div><div class='flex-row top col-xs-9'><div class='analysis-percentage'><br>LOW</div><div class='percent'></div><div class='analysis-text'><b>Less than 50%</b><br>Your invention likely covers patentable subject matter.</div></div><div class='col-xs-3'><div clas='risk-words'><div style='display:inline-block;'><div class='subtitle'>At&nbsp;Risk&nbsp;Words</div><hr style='border-top-color:#88a3b5;border-top-width:2px;'></div><br>None</div></div></div></div><hr style='border-top-color:#88a3b5;'>";
    		$(".analysis_holder","#container-step4").html(analysis_html);
    		nlpapp_hide_loader_modal();
    	} else {
    		if( data.high_tech !== null){
    			var risk_words_html = "";
    			var risk_words = data.high_tech.at_risk;
    			for(w=0;w<risk_words.length;w++){
    				risk_words_html = risk_words_html + risk_words[w] + "<br>";
    			}
    			if (data.high_tech.p >= 80 ){
    				risk_color = "high";
    			} else {
    				risk_color = "med";
    			}
    			analysis_html = analysis_html + "<div class='analysis-result " + risk_color + "'><div class='row'><div class='col-xs-9'><b>Likelihood of a s. 101 rejection by the USPTO</b><br><br></div><div class='col-xs-3'></div><div class='flex-row top col-xs-9'><div class='analysis-percentage'><br>" + data.high_tech.p + "</div><div class='percent'>%</div><div class='analysis-text'>This number is especially relevant if your invention is related to software, business methods, DNA sequencing, or medical diagnostics.</div></div><div class='col-xs-3'><div clas='risk-words'><div style='display:inline-block;'><div class='subtitle'>At&nbsp;Risk&nbsp;Words</div><hr style='border-top-color:#88a3b5;border-top-width:2px;'></div><br>" + risk_words_html + "</div></div></div></div><hr style='border-top-color:#88a3b5;'>";
    		}
    		if( data.life_sciences !== null){
    			var risk_words_html = "";
    			var risk_words = data.life_sciences.at_risk;
    			for(w=0;w<risk_words.length;w++){
    				risk_words_html = risk_words_html + risk_words[w] + "<br>";
    			}
    			if (data.life_sciences.p >= 80 ){
    				risk_color = "high";
    			} else {
    				risk_color = "med";
    			}
    			analysis_html = analysis_html + "<div class='analysis-result " + risk_color + "'><div class='row'><div class='col-xs-9'><b>Likelihood of a s. 101 rejection by the USPTO</b><br><br></div><div class='col-xs-3'></div><div class='flex-row top col-xs-9'><div class='analysis-percentage'><br>" + data.life_sciences.p + "</div><div class='percent'>%</div><div class='analysis-text'>This number is especially relevant if your invention is related to software, business methods, DNA sequencing, or medical diagnostics.</div></div><div class='col-xs-3'><div clas='risk-words'><div style='display:inline-block;'><div class='subtitle'>At&nbsp;Risk&nbsp;Words</div><hr style='border-top-color:#88a3b5;border-top-width:2px;'></div><br>" + risk_words_html + "</div></div></div></div><hr style='border-top-color:#88a3b5;'>";
    		}
    		$(".analysis_holder","#container-step4").html(analysis_html);
    		nlpapp_hide_loader_modal();
    	}

    }
	// ---------------------------------------------------------------
	// email analysis button
	// ---------------------------------------------------------------
	$(document.body).on("click", "#nlpapp-email-analysis", function(){
		ajaxCall( nlp_dataroute.analysis_email, "GET", "", nlpapp_email_analysis_complete, "#nlpapp-analysis-save", null, "PREPARING SUMMARY...");
	});
	function nlpapp_email_analysis_complete(data){
		$(".form-feedback","#nlpapp-analysis-save").addClass("SUCCESS").text( data[Object.keys(data)[0]] ).show();
		nlpapp_hide_loader_modal();
		console.log("email successful");
        console.log(data);
	}
	// ---------------------------------------------------------------
	// download analysis button saved
	// ---------------------------------------------------------------
	$(document.body).on("click", "#nlpapp-download-analysis-saved button", function(){
		ajaxCall( nlp_dataroute.step3_download_saved, "GET", "", nlpapp_download_analysis_complete, "#nlpapp-analysis-save", null, "PREPARING SUMMARY...");
	});
	function nlpapp_download_analysis_complete(data){
		nlpapp_hide_loader_modal();
		if(data.prior_art_saved !== null){
			// they have saved prior art so we submit the hidden form to download
			// attach rnd to download action to prevent caching
			$("#nlpapp-download-analysis-hidden").attr( "action" , "/downloadresults?r="+new Date().getTime() ).submit();

			//
			//$("#nlpapp-download-analysis-hidden").submit();
			console.log("download successful");
		} else {
			$(".form-feedback","#nlpapp-analysis-save").addClass("with-errors").text( "You have not saved any Prior Art results." ).show();
		}
	}
	// ---------------------------------------------------------------
	// download analysis button results
	// ---------------------------------------------------------------
	$(document.body).on("click", "#nlpapp-download-analysis-results", function(){
		ajaxCall( nlp_dataroute.step3_download_all, "GET", "", nlpapp_download_analysis_complete, "#nlpapp-priorart-found-col", null, "PREPARING SUMMARY...");
	});
	function nlpapp_download_analysis_complete(data){
		nlpapp_hide_loader_modal();
		if(data.prior_art_saved !== null){
			// they have saved prior art so we submit the hidden form to download
			// attach rnd to download action to prevent caching
			$("#nlpapp-download-analysis-results-hidden").attr( "action" , "/downloadresults?r="+new Date().getTime() ).submit();
			console.log("download successful");
		} else {
			$(".form-feedback","#nlpapp-priorart-found-col").addClass("with-errors").text( "There are no results to download." ).show();
		}
	}
	// ---------------------------------------------------------------
	// filters submit
	// ---------------------------------------------------------------
	$(document.body).on("click", "#nlpapp-filters-apply", function(){
		if ( !$(this).hasClass("disabled")){

		    validate_step_three_filters_form = nlpapp_validate_form_stepthree_filters();
		    if ( validate_step_three_filters_form === true ){

			    var key_elements_data="",results_elements_data="",cpc_sublcasses_data="",applicants_data="",from_date_data="",to_date_data="";
			    var key_elements_data_temp="",results_elements_data_temp="",cpc_sublcasses_data_temp="",applicants_data_temp="";
			    var filters_notification = "";
			    //if ( $("#key_elements","#nlpapp-filters-form").length ){
			    //	key_elements_data_temp = $("#key_elements","#nlpapp-filters-form").val();
			    //	if(!key_elements_data_temp==""){
			    //		key_elements_data = key_elements_data_temp.join(",");
			    //		filters_notification = filters_notification + "Key Elements : " + key_elements_data_temp.join(", ") + "<br>";
			    //	}
			    //}
			    var keyelement_number = $(".keyelement-field","#nlpapp-filters-form").length;
			    for(i=1;i<=keyelement_number;i++){
                    var element_value = $("#element_"+i,"#nlpapp-filters-form").val();
                    if ( element_value !== "" ){
                        key_elements_data = key_elements_data + "element_"+i+"=" + element_value + "&";
                    }
			    }
			    if ( $("#result_elements","#nlpapp-filters-form").length ){
			    	results_elements_data_temp = $("#result_elements","#nlpapp-filters-form").val();
			    	if(!results_elements_data_temp==""){
			    		results_elements_data = results_elements_data_temp.join(",");
			    		filters_notification = filters_notification + "Suggested Keywords : " + results_elements_data_temp.join(", ") + "<br>";
			    	}
			    }
			    if ( $("#cpc_subclasses","#nlpapp-filters-form").length ){
		    		cpc_sublcasses_data_temp = $("#cpc_subclasses","#nlpapp-filters-form").val();
			    	if(!cpc_sublcasses_data_temp==""){
			    		cpc_sublcasses_data = cpc_sublcasses_data_temp.join(",");
			    		filters_notification = filters_notification + "CPC Subclasses : " + cpc_sublcasses_data_temp.join(", ") + "<br>";
			    	}
			    }
				if ( $("#applicant_names","#nlpapp-filters-form").length ){
		    		applicants_data_temp = $("#applicant_names","#nlpapp-filters-form").val();
			    	if(!applicants_data_temp==""){
			    		applicants_data = applicants_data_temp.join(",");
			    		filters_notification = filters_notification + "Applicants : " + applicants_data_temp.join(", ") + "<br>";
			    	}
			    }
			    if ( $("#nlpapp-filters-fromdate","#nlpapp-filters-form").length ){
			    	temp_from_date = $("#nlpapp-filters-fromdate","#nlpapp-filters-form").datepicker("getDate");
			    	if(!temp_from_date==""){
			    		from_date_data = $.datepicker.formatDate("yy-mm-dd", temp_from_date);
			    		filters_notification = filters_notification + "From : " + from_date_data + "<br>";
			    	}
			    }
			    if ( $("#nlpapp-filters-todate","#nlpapp-filters-form").length ){
			    	temp_to_date = $("#nlpapp-filters-todate","#nlpapp-filters-form").datepicker("getDate");
			    	if(!temp_to_date==""){
			    		to_date_data = $.datepicker.formatDate("yy-mm-dd", temp_to_date);
			    		filters_notification = filters_notification + "To : " + to_date_data + "<br>";
			    	}
			    }
			    if( key_elements_data == null){ key_elements_data = "" };
			    if( results_elements_data == null){ results_elements_data = "" };
			    if( cpc_sublcasses_data == null){ cpc_sublcasses_data = "" };
				if( applicants_data == null){ applicants_data = "" };
			    var form_data = key_elements_data+"result_elements="+results_elements_data+"&cpc_subclasses="+cpc_sublcasses_data+"&applicants="+applicants_data+"&date_from="+from_date_data+"&date_to="+to_date_data;
			    if( form_data == "result_elements=&cpc_subclasses=&applicants=&date_from=&date_to="){
			    	$("#nlpapp-filters-notification").html("").hide();
			    	// reload
			    	nlpapp_load_stepthree_results();
			    } else {
			    	$("#nlpapp-filters-notification").html(filters_notification).show();
			    	nlpapp_load_stepthree_filtered_results(form_data);
			    }
		    }
		}
	});
	// ---------------------------------------------------------------
	// validate step 3 filters key_elements
	// ---------------------------------------------------------------
	function nlpapp_validate_form_stepthree_filters(){
	    var stepthree_form = "#nlpapp-filters-form";
	    var stepthree_form_valid = true;
	    // regexp's
	    keyelement_regexp = new RegExp("^\\w+(?:\\s+\\w+){0,4}$");
        // validate key elements (if entered)
        // ---------------------------------------------------------------
        var keyelement_error = "Must be a maximum of 5 words.";
        var keyelement_number = $(".keyelement-field",stepthree_form).length;
        for(i=1;i<=keyelement_number;i++){
  	       var element_value = $("#element_"+i,stepthree_form).val();
  	        if ( element_value !== "" ){
  		        // theve entered a key element so we test it
  		        if ( keyelement_regexp.test(element_value) === false ){
  		        	stepthree_form_valid = false;
  		        	$("#element_"+i,stepthree_form).siblings(".help-block").text(keyelement_error).show();
  		        } else {
  		        	$("#element_"+i,stepthree_form).siblings(".help-block").text("").hide();
  		        }
  	        }
        }
        return stepthree_form_valid;
    }
	// ---------------------------------------------------------------
	// filters clear
	// ---------------------------------------------------------------
	$(document.body).on("click", "#nlpapp-filters-clear", function(){
		if ( !$(this).hasClass("disabled")){
			stepthree_filters_clear();
			// reload
			nlpapp_load_stepthree_results();
		}
	});
	function stepthree_filters_clear(){
		$("#nlpapp-filters-notification").html("").hide();
		$("#key_elements","#nlpapp-filters-form").multiselect("reset");
		$("#result_elements","#nlpapp-filters-form").multiselect("reset");
		$("#cpc_subclasses","#nlpapp-filters-form").multiselect("reset");
		$("#applicants","#nlpapp-filters-form").multiselect("reset");
		$("#nlpapp-filters-fromdate","#nlpapp-filters-form").datepicker('setDate', null);
		$("#nlpapp-filters-todate","#nlpapp-filters-form").datepicker('setDate', null);
		$(".help-block,.form-feedback","#container-step3").text("");
	}
	// ---------------------------------------------------------------
	// update results submit
	// ---------------------------------------------------------------
	$(document.body).on("click", "#nlpapp-update-results", function(){
		if ( !$(this).hasClass("disabled")){
			var saved_results = new Array();
			$("tbody tr:not(.empty-row-message)","#prior-art-saved-results-table").each(function(){
				saved_results.push( $(this).attr("data-id") + ":" + $(this).attr("data-cpc") );
			});
			var form_data = "saved_results=" + saved_results.join(",");
			nlpapp_load_stepthree_updated_results(form_data);
		}
	});
	// ---------------------------------------------------------------
	// clear updated results submit
	// ---------------------------------------------------------------
	$(document.body).on("click", "#nlpapp-clearupdated-results", function(){
		if ( !$(this).hasClass("disabled")){
			nlpapp_load_stepthree_clearupdated_results();
		}
	});

	// ---------------------------------------------------------------
	// remove saved prior art
	// ---------------------------------------------------------------
	$(document.body).on("click", ".nlpapp-priorart-removesaved", function(){
		// setup modal confirmation
		var target_modal = $("#nlpapp-modal-delete-savedpriorart");
		target_modal.find("#delete-savedpriorart-id").text( $(this).parent().parent().attr("data-id") );
		target_modal.find("#delete-savedpriorart-confirm").attr("data-id", $(this).parent().parent().attr("data-id")).attr("data-cpc", $(this).parent().parent().attr("data-cpc") );
		// turn on modal
		target_modal.modal({backdrop: 'static'});
	});
	// remove saved prior art confirmation (from modal)
	// ---------------------------------------------------------------
	$("#delete-savedpriorart-confirm").click(function(){
		var priorart_id = $(this).attr("data-id");
		// delete it
		form_data = "p="+ $(this).attr("data-id")+"&c="+ $(this).attr("data-cpc");
		ajaxCall( nlp_dataroute.step3_remove_result, "POST", form_data, nlpapp_stepthree_deletesaveresult_complete, "application", null, "PROCESSING...");
	});
	function nlpapp_stepthree_deletesaveresult_complete(){
		if ( $("#prior-art-results-table").hasClass("filtered-results") ){
			nlpapp_load_stepthree_results_filtered();
		} else {
			nlpapp_load_stepthree_results("relay_true");
		}
		nlpapp_load_stepthree_savedresults("relay_true");
	}
	// ---------------------------------------------------------------
	// save prior art (add to save prior art list)
	// ---------------------------------------------------------------
	$(document.body).on("click", ".nlpapp-priorart-save", function(){
		if ( !$(this).hasClass("disabled")){
			form_data = "p="+ $(this).parent().parent().attr("data-id")+"&c="+ $(this).parent().parent().attr("data-cpc");
			ajaxCall( nlp_dataroute.step3_save_result , "POST", form_data, nlpapp_stepthree_saveresult_complete, ".addsavedpriorart-row", null, "PROCESSING...");
			check_priorart_table("prior-art-results-table");
		}
	});
	function nlpapp_stepthree_saveresult_complete(){
		// check if we are viewing a filtered prior list, or normal prior list
		if ( $("#prior-art-results-table").hasClass("filtered-results") ){
			nlpapp_load_stepthree_results_filtered();
		} else {
			nlpapp_load_stepthree_results("relay_true");
		}
		nlpapp_load_stepthree_savedresults("relay_true");
	}
	// ---------------------------------------------------------------
	// delete prior art result (remove from prior art list)
	// ---------------------------------------------------------------
	$(document.body).on("click", ".nlpapp-priorart-delete", function(){
		if ( !$(this).hasClass("disabled") ){
			// setup modal confirmation
			var target_modal = $("#nlpapp-modal-delete-priorartresult");
			target_modal.find("#delete-priorartresult-id").text( $(this).parent().parent().attr("data-id") );
			target_modal.find("#delete-priorartresult-confirm").attr("data-id", $(this).parent().parent().attr("data-id") ).attr("data-cpc", $(this).parent().parent().attr("data-cpc"));
			// turn on modal
			target_modal.modal({backdrop: 'static'});
		}
	});
	// delete prior art confirmation (from modal)
	// ---------------------------------------------------------------
	$("#delete-priorartresult-confirm").click(function(){
		var priorart_id = $(this).attr("data-id");
		// delete it
		form_data = "p="+ $(this).attr("data-id")+"&c="+ $(this).attr("data-cpc");
		ajaxCall( nlp_dataroute.step3_delete_result, "POST", form_data, nlpapp_stepthree_deleteresult_complete, "application", null, "PROCESSING...");
	});
	function nlpapp_stepthree_deleteresult_complete(data,callback){
		if ( $("#prior-art-results-table").hasClass("filtered-results") ){
			nlpapp_load_stepthree_results_filtered("relay_true");
		} else {
			nlpapp_load_stepthree_results("relay_true");
		}
	}
	// ---------------------------------------------------------------
	// ---------------------------------------------------------------
	// profile & manage project functions
	// ---------------------------------------------------------------
	// ---------------------------------------------------------------
	// ---------------------------------------------------------------
	// Project Select Widget Buttons
	// ---------------------------------------------------------------
	// change project button toggles
	// ---------------------------------------------------------------
	$( "#nlpapp_changeproject" ).click(function(event) {
		event.preventDefault();
		// post data
		ajaxCall( nlp_dataroute.all_projects_load , "GET", "", nlpapp_load_all_projects , "application");
	});
	function nlpapp_load_all_projects(data){
		$("input[type=text]","#project-select").val("");
		$(".help-block,.form-feedback","#project-select").text("");
		$(".form-feedback","#project-select").hide();
		$("input[type=text]","#project-select-create").val("");
		$(".help-block,.form-feedback","#project-select-create").text("");
		$(".form-feedback","#project-select-create").hide();
		if ( data.projects !== null ){
			$("#nlpapp_changeselectedproject").parent().attr("data-name","").addClass("disabled");
			var nlpapp_numprojects = data.projects.length;
			var previously_saved_project_html = "";
			var active_flag = "";
			$(".project-select-holder").html("");
			for (p = 1; p <= nlpapp_numprojects; p++) {
				if ( data.projects[p-1].name == nlpapp_dataobject.current_project.name ){
					active_flag = "active";
				} else {
					active_flag = "";
				}
				previously_saved_project_html = "<div class='row project-select-entry " + active_flag + "' data-name='" + data.projects[p-1].name + "'><div class='col-xs-12 col-sm-6 project-select-name'>" + data.projects[p-1].name + "</div><div class='col-xs-12 col-sm-6 project-select-date text-xs-left text-sm-right'>" + data.projects[p-1].last_edited + "</div><div class='hex-button-small nlp-orange project-select-edit' data-num_searches='" + data.projects[p-1].num_searches + "' data-num_updates='" + data.projects[p-1].num_updates + "' data-security='" + data.projects[p-1].secure + "' data-name='" + data.projects[p-1].name + "' style='min-width:0;'><button type='submit' class='btn btn-primary nlpapp-button' id='nlpapp_cancelchangeproject'>Edit</button></div></div></div>"
				$(".project-select-holder").append( previously_saved_project_html );
			}
			$(".project-select-saved").show();
			$(".container-body").hide();
			$("#project-select","#header-application").show();
			$("#nlpapp_changeproject").parent().hide();
			$("#nlpapp_cancelchangeproject").parent().show();
			nlpapp_hide_loader_modal();
		} else {
			$(".project-select-saved").hide();
			$(".container-body").hide();
			$("#project-select","#header-application").show();
			$("#nlpapp_changeproject").parent().hide();
			$("#nlpapp_cancelchangeproject").parent().show();
			nlpapp_hide_loader_modal();
		}
	}
	$( "#nlpapp_cancelchangeproject").click(function() {
		$("#body-application").show();
		$("#project-select","#header-application").hide();
		$("#nlpapp_changeproject").parent().show();
		$("#nlpapp_cancelchangeproject").parent().hide();
		// if we are on /step1 or /step1_security_check recall change project to force recheck of security
		var referring_route = nlp_router.lastRouteResolved().url;
		if (referring_route == "step1" || referring_route == "step1_security_check"){
			nlp_router.navigate("#change_project?newproject=false");
		}
	});


	// select project from project widget
	// ---------------------------------------------------------------
	$(document.body).on("click", ".project-select-entry", function(){
		$(".project-select-entry").removeClass("active");
		$(this).addClass("active");
		var clicked_project = $(this).attr("data-name");
		//console.log( clicked_project + " : " + nlpapp_dataobject.current_project.name );
		if ( clicked_project != nlpapp_dataobject.current_project.name ){
			//console.log("shows");
			$("#nlpapp_changeselectedproject").parent().attr("data-name",clicked_project).removeClass("disabled");
		} else {
			//console.log("hides");
			$("#nlpapp_changeselectedproject").parent().attr("data-name","").addClass("disabled");
		}
	});
	// change project click
	// ---------------------------------------------------------------
	$(document.body).on("click", "#nlpapp_changeselectedproject", function(event){
		if ( !$(this).parent().hasClass("disabled") ){
			event.preventDefault();
			var form_data = "project_name=" + $(this).parent().attr("data-name");
			// post data
			ajaxCall( nlp_dataroute.current_project_submit , "POST", form_data, nlpapp_load_currentproject, ".project-select-saved" );
		}
	});

	// ---------------------------------------------------------------
	// edit project click
	// ---------------------------------------------------------------
	$(document.body).on("click", ".project-select-edit", function(event){
		// setup modal confirmation
		var target_modal = $("#nlpapp-modal-edit-project");
		target_modal.find("#edit-project-name").text( $(this).attr("data-name") );
		// monthly usage
		target_modal.find("#nlpapp_monthly_searches").html( $(this).attr("data-num_searches") )
		target_modal.find("#nlpapp_monthly_updates").html( $(this).attr("data-num_updates") )
		// edit project name
		target_modal.find("#old_name").val( $(this).attr("data-name") );
		target_modal.find("#new_name").attr("placeholder", $(this).attr("data-name") ).val("");
		// change project security
		target_modal.find("input[name=project_name]").val( $(this).attr("data-name") );
		target_modal.find("input[name=security][value=" +  $(this).attr("data-security") + "]").prop("checked",true);

		// delete project
		target_modal.find("input[name=project_name]").val( $(this).attr("data-name") );
		// turn off confirm delete button to reset it
		target_modal.find("#nlpapp_delete_project_button_confirm").parent().hide();
		target_modal.find("#nlpapp_delete_project_button_cancel").parent().hide();

		// can only do the following check when we're editing the current project
		if ( $(this).attr("data-name") == nlpapp_dataobject.current_project.name ){
			// determine if edit security settings will be disabled or not
			if ( nlpapp_dataobject.current_project.secure == 1 && nlpapp_dataobject.security_unlocked == 0 ){
				$(".hex-button-small","#nlpapp_edit_project_security").addClass("disabled");
				$("input,button","#nlpapp_edit_project_security").prop('disabled', true);
				$("label","#nlpapp_edit_project_security").css('opacity', '0.5');
				$("#nlpapp_edit_project_security_lockednotification,#nlpapp_edit_project_security_lockednotification .help-block","#nlpapp_edit_project_security").show();

			} else if ( ( nlpapp_dataobject.current_project.secure == 1 && nlpapp_dataobject.security_unlocked == 1 ) ||  nlpapp_dataobject.current_project.secure == 0){
				$(".hex-button-small","#nlpapp_edit_project_security").removeClass("disabled");
				$("input,button","#nlpapp_edit_project_security").prop('disabled', false);
				$("label","#nlpapp_edit_project_security").css('opacity', '1.0');
				$("#nlpapp_edit_project_security_lockednotification,#nlpapp_edit_project_security_lockednotification .help-block","#nlpapp_edit_project_security").hide();
			}
		} else {
			// we're editing another project
			if ( $(this).attr("data-security") == 1 ){
				$(".hex-button-small","#nlpapp_edit_project_security").addClass("disabled");
				$("input,button","#nlpapp_edit_project_security").prop('disabled', true);
				$("label","#nlpapp_edit_project_security").css('opacity', '0.5');
				$("#nlpapp_edit_project_security_lockednotification,#nlpapp_edit_project_security_lockednotification .help-block","#nlpapp_edit_project_security").show();
			} else {
				$(".hex-button-small","#nlpapp_edit_project_security").removeClass("disabled");
				$("input,button","#nlpapp_edit_project_security").prop('disabled', false);
				$("label","#nlpapp_edit_project_security").css('opacity', '1.0');
				$("#nlpapp_edit_project_security_lockednotification,#nlpapp_edit_project_security_lockednotification .help-block","#nlpapp_edit_project_security").hide();
			}
		}
		// turn on modal
		target_modal.modal({backdrop: 'static'});
	});
	$('#nlpapp-modal-edit-project').on('hidden.bs.modal', function(event) {
		$("input[type=text],select","#nlpapp-modal-edit-project").val("");
		$(".help-block,.form-feedback","#nlpapp-modal-edit-project").text("");
		$(".form-feedback","#nlpapp-modal-edit-project").hide();
	});
	// ---------------------------------------------------------------
	// Edit Project Name (from project select)
	// ---------------------------------------------------------------
	$( "#nlpapp_edit_project_name" ).submit(function(event) {
		event.preventDefault();
		validate_edit_project_name_form = nlpapp_validate_form_renameproject();
		///window.alert(validate_step_one_form);
		if ( validate_edit_project_name_form === true ){
			var form_data = ajaxSerializeForm("#nlpapp_edit_project_name");
			// post data
			ajaxCall( nlp_dataroute.rename_project_submit , "POST", form_data, nlpapp_edit_project_name_complete , "#nlpapp_edit_project_name");
		}
	});
	function nlpapp_edit_project_name_complete(data){
		$('#nlpapp-modal-edit-project').modal('hide');
		// call load project info again
		nlpapp_load_currentproject();
	}

	// ---------------------------------------------------------------
	// Edit Project Security (from project select)
	// ---------------------------------------------------------------
	$( "#nlpapp_edit_project_security" ).submit(function(event) {
		event.preventDefault();
		var form_data = ajaxSerializeForm("#nlpapp_edit_project_security");
		ajaxCall( nlp_dataroute.setproject_security_submit , "POST", form_data, nlpapp_edit_project_security_complete , "#nlpapp_edit_project_security");
	});
	function nlpapp_edit_project_security_complete(data){
		// reload current project security, just incase they edited the current project
		ajaxCall( nlp_dataroute.current_project_load, "GET", "", nlpapp_load_currentproject_setdata, "application", nlpapp_edit_project_security_complete_refresh, "");
	}
	function nlpapp_edit_project_security_complete_refresh(data){
		$('#nlpapp-modal-edit-project').modal('hide');
		// call load project info again
		ajaxCall( nlp_dataroute.all_projects_load , "GET", "", nlpapp_load_all_projects , "application");
	}
	// ---------------------------------------------------------------
	// Delete Project (from project select)
	// ---------------------------------------------------------------
	$(document.body).on("click", "#nlpapp_delete_project_button_initial", function(event){
		// first step of deleting a project
		$("#nlpapp_delete_project_button_confirm").parent().fadeIn(500);
		$("#nlpapp_delete_project_button_cancel").parent().fadeIn(500);
		$("#nlpapp_delete_project_button_initial").parent().hide();
	});
	$(document.body).on("click", "#nlpapp_delete_project_button_cancel", function(event){
		event.preventDefault();
		$("#nlpapp_delete_project_button_initial").parent().show();
		$("#nlpapp_delete_project_button_cancel").parent().hide();
		$("#nlpapp_delete_project_button_confirm").parent().hide();
	});
	$(document.body).on("click", "#nlpapp_delete_project_button_confirm", function(event){
		event.preventDefault();
		var form_data = ajaxSerializeForm("#nlpapp_delete_project");
		if ( $("input[name=project_name]","#nlpapp_delete_project").val() !== nlpapp_dataobject.current_project.name){
			// post data
			ajaxCall( nlp_dataroute.remove_project_submit , "POST", form_data, nlpapp_remove_otherproject_complete , "#nlpapp_delete_project");
		} else {
			ajaxCall( nlp_dataroute.remove_project_submit , "POST", form_data, nlpapp_remove_currentproject_complete , "#nlpapp_delete_project");
		}
	});
	function nlpapp_remove_currentproject_complete(data){
		$("#nlpapp_delete_project_button_initial").parent().show();
		$('#nlpapp-modal-edit-project').modal('hide');
		nlpapp_load_currentproject();
	}
	function nlpapp_remove_otherproject_complete(data){
		$("#nlpapp_delete_project_button_initial").parent().show();
		$('#nlpapp-modal-edit-project').modal('hide');
		// refresh project widget
		ajaxCall( nlp_dataroute.all_projects_load , "GET", "", nlpapp_load_all_projects , "application");
	}

	// ---------------------------------------------------------------
	// Create Project (from project select)
	// ---------------------------------------------------------------
	$( "#nlpapp_new_project" ).submit(function(event) {
		event.preventDefault();
		validate_new_project_form = nlpapp_validate_form_newproject();
		if ( validate_new_project_form === true ){
			var form_data = ajaxSerializeForm("#nlpapp_new_project");
			// post data
			ajaxCall( nlp_dataroute.add_project_submit, "POST", form_data, nlpapp_create_project_complete, "#nlpapp_new_project");
		}
	});
	function nlpapp_create_project_complete(data){
		$("#project-select","#header-application").hide();
		$(".project-select-saved").show();
		$("#nlpapp_changeproject").parent().show();
		$("#nlpapp_cancelchangeproject").parent().hide();
		nlpapp_load_currentproject();
	}
	// ---------------------------------------------------------------
	// Create Project (from create onlogin)
	// ---------------------------------------------------------------
	$( "#nlpapp_new_project_create" ).submit(function(event) {
		event.preventDefault();
		validate_new_project_form = nlpapp_validate_form_newproject_fromcreate();
		if ( validate_new_project_form === true ){
			var form_data = "project_name="+ $("#project_name_create","#nlpapp_new_project_create").val();
			// post data
			ajaxCall( nlp_dataroute.add_project_submit, "POST", form_data, nlpapp_create_project_fromcreate_complete, "#nlpapp_new_project_create");
		}
	});
	function nlpapp_create_project_fromcreate_complete(data){
		$("#project-select","#header-application").hide();
		$(".project-select-saved").show();
		$("#nlpapp_changeproject").parent().show();
		$("#nlpapp_cancelchangeproject").parent().hide();
		nlpapp_load_currentproject();
	}

	// ---------------------------------------------------------------
	// Profile / Edit Profile
	// ---------------------------------------------------------------
	function nlpapp_load_editprofile(){
		nlapp_reset_ui();
		ajaxCall( nlp_dataroute.profile_load, "GET", "", nlpapp_load_profile_setdata, "application", nlpapp_editprofile_setup);
	}
	function nlpapp_editprofile_setup(){
		$("input[type=text],input[type=password],select","#container-profile_edit_profile").val("");
		$(".help-block,.form-feedback","#container-profile_edit_profile").text("");
		$(".form-feedback","#container-profile_edit_profile").hide();
		$(".row-header-welcome").text("Welcome back, "+ nlpapp_dataobject.user.first_name );
		$("#profile_email").val( nlpapp_dataobject.user.email );
		$("#profile_first_name").val( nlpapp_dataobject.user.first_name );
		$("#profile_last_name").val( nlpapp_dataobject.user.last_name );
		$("#profile_organization").val( nlpapp_dataobject.user.organization );
		$("#profile_role").val( nlpapp_dataobject.user.role );
		$("#profile_country").val( nlpapp_dataobject.user.country ).trigger('change');
		$("#profile_state").val( nlpapp_dataobject.user.region );
		//
		// check to see if there is a routed message to show
		nlpapp_check_root_message();
		//
		nlpapp_hide_loader_modal();
	}
	// ---------------------------------------------------------------
	// Profile / Edit Profile Submit
	// ---------------------------------------------------------------
	$( "#nlpapp_edit_profile" ).submit(function(event) {
		event.preventDefault();
		validate_changeprofile_form = nlpapp_validate_form_changeprofile();
		if ( validate_changeprofile_form === true ){
			var form_data = "first_name=" + $("#profile_first_name","#nlpapp_edit_profile").val() + "&last_name=" + $("#profile_last_name","#nlpapp_edit_profile").val() + "&role=" + $("#profile_role","#nlpapp_edit_profile").val() + "&country=" + $("#profile_country","#nlpapp_edit_profile").val() + "&region=" + $("#profile_state","#nlpapp_edit_profile").val();
			// post data
			ajaxCall( nlp_dataroute.edit_profile_submit , "POST", form_data, nlpapp_editprofile_complete , "#nlpapp_edit_profile");
		}
	});
	function nlpapp_editprofile_complete(data){
		nlpapp_hide_loader_modal();
		$(".form-feedback","#nlpapp_edit_profile").addClass("SUCCESS").text( data[Object.keys(data)[0]] ).show();
	}

	// ---------------------------------------------------------------
	// Profile / Change Password Submit
	// ---------------------------------------------------------------
	$( "#nlpapp_change_password" ).submit(function(event) {
		event.preventDefault();
		validate_changepassword_form = nlpapp_validate_form_changepassword();
		if ( validate_changepassword_form === true ){
			var form_data = "current_password=" + $("#profile_current_password","#nlpapp_change_password").val() + "&new_password=" + $("#profile_new_password","#nlpapp_change_password").val() + "&confirm_password=" + $("#profile_confirmnew_password","#nlpapp_change_password").val();
			// post data
			ajaxCall( nlp_dataroute.change_password_submit , "POST", form_data, nlpapp_changepassword_complete , "#nlpapp_change_password");
		}
	});
	function nlpapp_changepassword_complete(data){
		nlpapp_hide_loader_modal();
		$("input","#nlpapp_change_password").val("");
		// relay message for success
		nlpapp_root_message = [".form-feedback","#nlpapp_change_password","SUCCESS",data[Object.keys(data)[0]] ];
		$(".form-feedback","#nlpapp_change_password").text( data[Object.keys(data)[0]] ).show();
	}

	// ---------------------------------------------------------------
	// Profile / Plan Information
	// ---------------------------------------------------------------
	function nlpapp_load_profileplan(){
		nlapp_reset_ui();
		ajaxCall( nlp_dataroute.planinfo_load, "GET", "", nlpapp_load_profileplan_complete, "application", null);
		$(".row","#container-profile_plan_info").html("");
	}
	function nlpapp_load_profileplan_complete(data){
		var plan_html = "";
		if (data.client == "trial"){
			plan_html = "<div class='col-xs-12 text-xs-center'><br><br><br><br><br><div class='subtitle'>You are currently on a free Trial Account.<br><br>Please contact the Legalicity team at <a href='mailto:stephanie@legali.city' target='_new'>stephanie@legali.city</a> with any questions or to upgrade your account.</div> </div>";
			$(".row","#container-profile_plan_info").html(plan_html);
			nlpapp_hide_loader_modal();
		} else {
			ajaxCall( nlp_dataroute.currentusage_load, "GET", "", nlpapp_load_clientinfo, "application", null);
		}

	}
	function nlpapp_load_clientinfo(data){
		plan_usage = data.usage;
		plan_cap = data.cap;
		plan_expiry = data.expiry;
		if (plan_cap!==null) {
			plan_html = "<div class='col-xs-12 text-xs-left text-sm-center'><br><br><br><br><br>You are on the subscription plan for <b>" + nlpapp_dataobject.user.organization +"</b>. This plan expires on <i>" + plan_expiry +"</i>.<br><br>Your plan includes <b>up to " + plan_cap + "</b> searches and <b>free</b> unlimited updates of results.<br><br><br><br><br>";
		} else {
			plan_html = "<div class='col-xs-12 text-xs-left text-sm-center'><br><br><br><br><br>You are on the pay-per-search plan for <b>" + nlpapp_dataobject.user.organization +"</b>. Your organization will be charged monthly at the following rates:<br><table class='table' style='min-width:350px;width:50%;margin:2em auto;text-align:left;'><thead><tr><th>Action</th><th class='text-xs-right'>Price</th></tr></thead><tbody><tr><td>Perform a new search:</td><td class='text-xs-right'>$" + nlpapp_dataobject.user.search_cost + "&nbsp;&nbsp;</td></tr><tr><td>Update search results:</td><td class='text-xs-right'>$" + nlpapp_dataobject.user.update_cost + "&nbsp;&nbsp;</td></tr></tbody></table>"
		}
		if ( nlpapp_dataobject.user.admin == 1){
			if(plan_cap!==null){
				plan_cap = parseInt(plan_cap);
				cap_usage_percentage = Math.floor((plan_usage / plan_cap) * 100);
				plan_usage_display = numberWithCommas(plan_usage);
				plan_cap_display = numberWithCommas(plan_cap);
				cap_usage_html = "<div class='capusage text-xs-center'><div class='progress'><div class='progress-bar progress-bar-warning' role='progressbar' aria-valuenow='" + plan_usage + "' aria-valuemin='0' aria-valuemax='"+plan_cap+"' style='width: " + cap_usage_percentage + "%;'><span class='sr-only'>" + cap_usage_percentage + "% Cap Used</span></div><br><br></div><div class='subtitle'>" + plan_usage_display + " / " + plan_cap_display +" Searches Used</div></div>";
			} else {
				plan_usage_display = numberWithCommas(plan_usage);
				cap_usage_html = "<div class='capusage text-xs-center'><div class='progress'><div class='progress-bar progress-bar-warning' role='progressbar' aria-valuenow='" + plan_usage + "' aria-valuemin='0' style='width: 5%;'></div><br><br></div><div class='subtitle'>$" + plan_usage_display + "</div></div>";
			}
			if ( nlpapp_dataobject.user.payment_method!==null && nlpapp_dataobject.user.payment_number!==null && nlpapp_dataobject.user.payment_expiry!==null){
			    // custom stripe method
				if (plan_cap!==null) {
					cap_html_description = "Below is the summary of your organization's usage:"
				} else {
					cap_html_description = "Your organization's usage for this month so far:"
				}
				cap_html = "<div class='col-xs-12 col-sm-7 text-xs-left'><div class='hidden-sm hidden-md hidden-lg hidden-xl'><br><br></div><div class='subtitle'>Usage</div><hr><p>"+ cap_html_description + "</p><br>" + cap_usage_html + "<br><div class='subtitle'>Payment Method</div><hr><div class='row flex-row middle'><div class='col-xs-12 col-sm-6 text-xs-center' style='line-height:150%;'><p>Currently Using : <b>" + nlpapp_dataobject.user.payment_method + "</b><br>Ending in&nbsp;:&nbsp;<b>" + nlpapp_dataobject.user.payment_number + "</b>&nbsp;&nbsp; Expiry&nbsp;:&nbsp;<b>" + nlpapp_dataobject.user.payment_expiry + "</b></p></div><div class='col-xs-12 col-sm-6 text-xs-center text-sm-left'><div class='hex-button nlp-orange'><button type='submit' class='btn btn-primary' id='change_payment'>Change Payment Method</button></div></div></div><div id='nlpapp_changepayment'><form><div class='form-feedback'></div></form></div></div></div></div>"
			} else {
			    // invoicing method
				if (plan_cap!==null) {
					cap_html_description = "Below is the summary of your organization's usage:"
				} else {
					cap_html_description = "Your organization's usage for this month so far:"
				}
			    cap_html = "<div class='col-xs-12 col-sm-7 text-xs-left'><div class='hidden-sm hidden-md hidden-lg hidden-xl'><br><br></div><div class='subtitle'>Usage</div><hr><p>"+ cap_html_description + "</p><br>" + cap_usage_html + "<br><div class='subtitle'>Payment Method</div><hr><div class='row flex-row middle'><div class='col-xs-12' style='line-height:150%;'><p><b>Cheque / Direct Deposit</b><br></p></div></div></div></div></div>";
			}

			// retrieve emails for account
			$.ajax({
                    url: nlp_dataroute.useraccounts_load,
                    type: "GET",
                    data: "",
                    //crossDomain: true,
                    //xhrFields: { withCredentials: true },
                    dataType: 'json',
                    success: function(response_data) {
                    	// admin emails
                    	// ---------------------------------------------------------------
                    	var account_mails = "</div><div class='col-xs-12 col-sm-5'><div class='subtitle'>User Accounts</div><hr><p>Below are the accounts associated with <b>" + nlpapp_dataobject.user.organization +"</b>.</p><table class='table'><thead><tr><th>Administrator Accounts</th></tr>";
                    	for(a=0;a<response_data.admin.length;a++){
                    		account_mails = account_mails + "<tr><td>" + response_data.admin[a] + "</td></tr>";
                    	}
                    	if( response_data.admin.length < 1){
                    		account_mails = account_mails + "<tr><td>None</td></tr>";
                    	}
                    	account_mails = account_mails + "</table><br>";
                    	// user emails
                    	// ---------------------------------------------------------------
                    	var user_mails = "<table class='table'><thead><tr><th>Regular Accounts</th></tr>";
                    	for(a=0;a<response_data.regular.length;a++){
                    		user_mails = user_mails + "<tr><td>" + response_data.regular[a] + "</td></tr>";
                    	}
                    	if( response_data.regular.length < 1){
                    		user_mails = user_mails + "<tr><td>None</td></tr>";
                    	}
                    	user_mails = user_mails + "</table></div>";
                    	plan_html = plan_html + account_mails + user_mails + cap_html;
                    	//
					$(".row","#container-profile_plan_info").html(plan_html);

					// check to see if there is a routed message to show
					nlpapp_check_root_message();
                    if ( nlpapp_dataobject.user.payment_method!==null && nlpapp_dataobject.user.payment_number!==null && nlpapp_dataobject.user.payment_expiry!==null){

					    // stripe change payment
					    var handler = StripeCheckout.configure({
		                    key : nlpapp_dataobject.user.stripe_key,
		                    name: 'NLPatent',
		                    image: 'static/images/nlpapp_icon_stripe.jpg',
		                    description: 'Change Payment Method',
		                    panelLabel: 'Update',
		                     token: function(token) {
		                        // send data
		                        ajaxCall( nlp_dataroute.change_payment, "POST", "stripeEmail=" + token.email + "&stripeToken="+ token.id, nlpapp_change_payment_complete, "#nlpapp_changepayment", null);
		                    }
		              	    });
		              	    // stripe button handlers
                            	document.getElementById('change_payment').addEventListener('click', function(e) {
                            		e.preventDefault();
                            		// open stripe panel
                                handler.open();
                            	});
                            	// Close Checkout on page navigation:
                            	window.addEventListener('popstate', function() {
                             handler.close();
                            	});
                    }
					nlpapp_hide_loader_modal();
                    },
				error: function(response_data) {
					nlpapp_hide_loader_modal();
					$('#nlpapp-errormsg').modal('show');
				}
			});
		} else {
			plan_html = plan_html+"Please contact an Administrator within your organization for more information.";
			$(".row","#container-profile_plan_info").html(plan_html);
			nlpapp_hide_loader_modal();
		}
	}
	//
	function nlpapp_change_payment_complete(data){
		// relay message for success
		nlpapp_root_message = [".form-feedback","#nlpapp_changepayment","SUCCESS",data[Object.keys(data)[0]] ];
		// load new profile info
		ajaxCall( nlp_dataroute.profile_load, "GET", "", nlpapp_load_profile_setdata, "application", nlpapp_change_payment_reload);
	}
	function nlpapp_change_payment_reload(data){
		ajaxCall( nlp_dataroute.currentusage_load, "GET", "", nlpapp_load_clientinfo, "application", null);
	}

	// ---------------------------------------------------------------
	// Profile / Change Cap Amount Submit
	// ---------------------------------------------------------------
	$(document.body).on("click", "[id=changecap_submit]", function(event) {
		$(".form-feedback","#nlpapp_change_usagecap").text("");
		event.preventDefault();
		validate_changecap_form = nlpapp_validate_form_changecap( $("#change_cap").attr("data-currentusage") );
		if ( validate_changecap_form === true ){
			var form_data = "new_cap=" + $("#change_cap","#nlpapp_change_usagecap").val();
			// post data
			ajaxCall( nlp_dataroute.capusage_set , "POST", form_data, nlpapp_changecap_complete , "#nlpapp_change_usagecap");
		}
	});
	function nlpapp_changecap_complete(data){
		nlpapp_hide_loader_modal();
		$("#change_cap","#nlpapp_change_usagecap").val("");
		// relay message for success
		nlpapp_root_message = [".form-feedback","#nlpapp_change_usagecap","SUCCESS",data[Object.keys(data)[0]] ];
		$(".form-feedback","#nlpapp_change_usagecap").text( data[Object.keys(data)[0]] ).show();
		nlpapp_load_profileplan( $(".form-feedback","#nlpapp_change_usagecap").text() );
	}


	//
	// ---------------------------------------------------------------
	// form helper function for serializing form data
	// ---------------------------------------------------------------
	function ajaxSerializeForm(form){
		var form_data = $(form).serialize();
		return form_data;
	}
	// helper for checkboxes used in steps 2a, 2b and 3
	function ajaxSerializeCheckboxes(form){
		var form_data = $(form).serializeArray();
		return form_data;
	}
	// function for data posting and retrieval
	// ---------------------------------------------------------------
	function ajaxCall(url, type, data, setter, caller, callback, message) {
		// hide form-feedback errors, if any
		$(".form-feedback", caller).removeClass("SUCCESS FIELDLEVEL_ERROR ERROR EXISTS FAIL DENIED MISSING PAYMENT_ERROR").text("").hide();
		nlpapp_show_loader_modal(message);
		nlpapp_ajax_active = true;

		// core AJAX objects
		// url = data of route to load
		// type = GET/POST
		// data = data to be sent, var or ""
		// setter = data setter function - sets data, or if callback is blank, handles the return route too
		// caller = caller object, expressly used to showing errors
			// application - errors are handled by the generic overlay error message
			// route
			// #object - transfers errors back to jquery object, for showing
		// callback = this is a passthrough function which once the setter succeeds is fired
			// - typically a view function for changing frontend
		// message - what to display on the loading modal overlay while this route loads
		var urlRand = new Date().getTime();
		$.ajax({
			url: url,
			type: type,
			data: data,
			//crossDomain: true,
	        //xhrFields: { withCredentials: true },
			dataType: 'json',
			success: function(response_data) {
				var success_msg = Object.keys(response_data)[0];
				if ( success_msg == "TIMEOUT" ){
					// timeout
					nlpapp_root_message = [".form-feedback","#nlpapp_login","SUCCESS","Your session has timed out." ];
					// navigate to login
					nlp_router.navigate("");
				} else if ( success_msg === "FIELDLEVEL_ERROR" || success_msg === "ERROR" || success_msg === "EXISTS" || success_msg === "FAIL" || success_msg === "DENIED" || success_msg === "MISSING" || success_msg === "PAYMENT_ERROR" ){
					// show errors msgs in forms
					if (success_msg == "FIELDLEVEL_ERROR"){
						var fieldlevel_error_object = response_data[Object.keys(response_data)[0]];
						var fieldlevel_error_num  = Object.keys(fieldlevel_error_object).length;
						for (i=0;i<fieldlevel_error_num;i++){
							$("#" + Object.keys(fieldlevel_error_object)[i],caller).siblings(".help-block").addClass("FIELDLEVEL_ERROR").text( fieldlevel_error_object[Object.keys(fieldlevel_error_object)[i]] ).show();
						}
						nlpapp_hide_loader_modal();
					} else {
						if (caller == "application"){
							// show generic error modal
							nlpapp_hide_loader_modal();
							$('#nlpapp-errormsg').find(".nlpapp-error-message").html("<br>" + response_data[Object.keys(response_data)[0]] );
							$('#nlpapp-errormsg').modal('show');
						} else if (caller == "route"){
							// pass variables back through setter, these are normally
							// only captured and shown in the router
							setter("error");
						} else {
							nlpapp_hide_loader_modal();
							$(".form-feedback", caller).addClass(success_msg).text( response_data[Object.keys(response_data)[0]] ).show();
							$(caller).siblings(".form-feedback").addClass(success_msg).text( response_data[Object.keys(response_data)[0]] ).show();
						}
					}
				} else if ( success_msg === "CAP_REACHED"){
					// show cap reached error
					nlpapp_hide_loader_modal();
					$(".nlpapp-error-message","#nlpapp-capreached").html("<br>"+ response_data[Object.keys(response_data)[0]] );
					$('#nlpapp-capreached').modal('show');

				} else {
					// complete setter - this will call setter and process data, then route to callback
					setter(response_data,callback);
				}
			},
			error: function(response_data) {
				nlpapp_hide_loader_modal();
				$('#nlpapp-errormsg').modal('show');
			}
		});
	}

	// set title of bootstrap mobile nav
	function nlpapp_update_mobilenav_title(title){
		$(".mobile-title").html(title);
	}
	// collapse navbar after click
	$(".navbar-collapse a").click(function(){
		$('.navbar-toggle').click();
	});

	// show content helper to turn on/off divs when navigating to a route
	// ---------------------------------------------------------------
	function show_application_page(holder,target){
		var nav_step_to_target = "";
		if (holder == "application"){
			if ( target == "step2a" || target == "step2b" ){
				//nav_step_to_target = "step2a";
				nav_step_to_target = "step2";
			} else {
				nav_step_to_target = target;
			}
			$("#header-application").show(); // show application header
			$("#header-login,#header-profile,#header-create").hide(); // hide login, profile header
			$("#body-application").show(); // show application body
			$("#body-login,#body-profile").hide(); // hide login, profile body
			$(".nav-tabs li, .navbar-nav li","#body-application").removeClass("active"); // turn off all navs in the navbars
			$(".nav-tabs li[id='nav-" + nav_step_to_target + "'], .navbar-nav li[id='mobilenav-" + nav_step_to_target + "']","#body-application").addClass("active"); // turn on navs
			$(".container-content").hide(); // turn on/off all content divs
			$("#container-" + target ).show(); // turn on target content div
			$(".container-footer").show();
			$("#mobilenav-" + nav_step_to_target + ",#nav-" + nav_step_to_target).show();
		} else if (holder == "profile"){
			$("#header-profile").show(); // show application header
			$("#header-login,#header-application,#header-create").hide(); // hide login, profile header
			$("#body-profile").show(); // show application body
			$("#body-login,#body-application").hide(); // hide login, profile body
			$(".nav-tabs li, .navbar-nav li","#body-profile").removeClass("active"); // turn off all navs in the navbars
			$(".nav-tabs li[id='nav-profile_" + target + "'], .navbar-nav li[id='mobilenav-profile_" + target + "']","#body-profile").addClass("active"); // turn on navs
			$(".container-content").hide(); // turn on/off all content divs
			$("#container-profile_" + target ).show(); // turn on target content div
			$(".container-footer").show();
			$("#mobilenav-profile_" + target + ",#nav-profile_" + target).show();
		} else if (holder == "login"){
			$("#header-login").show();
			$("#header-profile,#header-application,#header-create").hide();
			$("#body-profile,#body-application").hide();
			$(".nav-tabs li, .navbar-nav li").removeClass("active");
			$(".container-content").hide();
			$(".container-footer").show();
		} else if (holder == "create"){
			$("#header-create").show();
			$("#header-profile,#header-application,#header-login").hide();
			$("#body-profile,#body-application,#body-login").hide();
			$(".nav-tabs li, .navbar-nav li").removeClass("active");
			$(".container-content").hide();
			$(".container-footer").show();
		}
		window.scrollTo(0,0);
	}

	// ---------------------------------------------------------------
	// nlp_router definition and route directing
	// see : https://github.com/krasimir/navigo
	// ---------------------------------------------------------------
	var root = null;
	var useHash = true; // Defaults to: false
	var hash = '#'; // using # to remove issues of reloading errors
	var nlp_router = new Navigo(root, useHash, hash);
	nlp_router.on({
		'login': function () {
			nlapp_reset_ui();
			show_application_page("login","null");
			nlpapp_hide_loader_modal();
			// check to see if there is a routed message to show
			nlpapp_check_root_message();
		},
		'create_project':function(){
			show_application_page("create","");
			$("input[type=text]","#project-select-create").val("");
			$(".help-block,.form-feedback","#project-select-create").text("");
			$(".form-feedback","#project-select-create").hide();
			$("#project-select-create","#header-create").show();
			nlpapp_hide_loader_modal();
		},
		'change_project':function (params,query){
			// this is a route only to provide a stop between load, project edits and the steps
			// since we cannot reload a route easily or cleanly, this provides an
			// artificial separation of routes
			if ( query.newproject == true){
				// if its a new project, we clear the unlocked key for step security check to re-render
				nlpapp_dataobject.security_unlocked = 0;
			}
			$(".header-current-project-title").text( nlpapp_dataobject.current_project.name );
			$(".header-current-project-date").text( nlpapp_dataobject.current_project.last_edited );
			nlp_router.navigate("#step1");
		},
		'step1_security_check': function (){
			//security_unlocked
			$("#step1_locked","#container-step1").show();
			$("#step1_unlocked","#container-step1").hide();
			nlpapp_hide_loader_modal();
		},
		'step1': function () {
			if( nlpapp_dataobject.current_project.name == ""){
				nlp_router.navigate("#create_project");
			} else {
				show_application_page("application","step1");
				nlpapp_render_tabs();
				if ( nlpapp_dataobject.current_project.secure == 1 && nlpapp_dataobject.security_unlocked == 0 ){
					nlp_router.navigate("#step1_security_check");
					//security_unlocked
					$("#step1_locked","#container-step1").show();
					$("#step1_unlocked","#container-step1").hide();
				} else {
					//security_unlocked
					$("#step1_locked","#container-step1").hide();
					$("#step1_unlocked","#container-step1").show();
					nlpapp_update_mobilenav_title("Step 1 : Description");
					nlpapp_load_stepone();
				}
				//
				$("#project-select","#header-application").hide();
				$("#nlpapp_changeproject").parent().show();
				$("#nlpapp_cancelchangeproject").parent().hide();
			}
		},
		'step2_interim': function () {
			nlp_router.navigate("#step2");
		},
		'step2': function () {
			if( nlpapp_dataobject.current_project.name == ""){
				nlp_router.navigate("#create_project");
			} else {
				//redirect for step 2
				//nlp_router.navigate("#step2a");
				if ( nlpapp_dataobject.current_project.progress >=2 ){
					show_application_page("application","step2");
					nlpapp_update_mobilenav_title("Step 2 : Technology Areas");
					nlpapp_load_steptwo();
				} else {
					nlp_router.navigate("#step" + nlpapp_dataobject.current_project.progress);
				}
			}
		},
		'step2a_interim': function () {
			nlp_router.navigate("#step2a");
		},
		'step2a': function () {
			if( nlpapp_dataobject.current_project.name == ""){
				nlp_router.navigate("#create_project");
			} else {
				if ( nlpapp_dataobject.current_project.progress >=2 ){
					show_application_page("application","step2a");
					nlpapp_update_mobilenav_title("Step 2 : Technology Areas");
					nlpapp_load_steptwo_a();
				} else {
					nlp_router.navigate("#step" + nlpapp_dataobject.current_project.progress);
				}
			}
		},
		'step3': function () {
			if( nlpapp_dataobject.current_project.name == ""){
				nlp_router.navigate("#create_project");
			} else {
				if ( nlpapp_dataobject.current_project.progress >=3 ){
					show_application_page("application","step3");
					nlpapp_update_mobilenav_title("Step 3 : Prior Art");
					nlpapp_load_stepthree();
				} else {
					nlp_router.navigate("#step" + nlpapp_dataobject.current_project.progress);
				}
			}
		},
		'step4': function () {
			if( nlpapp_dataobject.current_project.name == ""){
				nlp_router.navigate("#create_project");
			} else {
				if ( nlpapp_dataobject.current_project.progress >=4 ){
					show_application_page("application","step4");
					nlpapp_update_mobilenav_title("Step 4 : Analysis");
					nlpapp_load_stepfour();
				} else {
					nlp_router.navigate("#step" + nlpapp_dataobject.current_project.progress);
				}
				nlpapp_hide_loader_modal();
			}
		},
		'profile_plan_info': function () {
			if ( nlpapp_dataobject.user.email !== "" ){
				show_application_page("profile","plan_info");
				nlpapp_update_mobilenav_title("Plan Information");
				nlpapp_load_profileplan();
			}
		},
		'profile_edit_profile': function () {
			if ( nlpapp_dataobject.user.email !== "" ){
				show_application_page("profile","edit_profile");
				nlpapp_update_mobilenav_title("Personal Information");
				nlpapp_load_editprofile();
			}
		},
		'profile': function () {
			nlp_router.navigate("#profile_edit_profile");
		},
		'logout': function () {
			nlpapp_logout();
		},
		'*': function () {
			nlapp_reset_ui();
			show_application_page("login","null");
			nlpapp_hide_loader_modal();
			// check to see if there is a routed message to show
			nlpapp_check_root_message();
		}
	});
	nlp_router.hooks({
		before: function (done, params) {
			nlpapp_show_loader_modal();
			// if there is no root user email (meaning theyre not logged in) we redirect to login
			// check performed on all routes
			if ( nlpapp_dataobject.user.email == "" ){
				done();
				nlp_router.navigate('');
			} else {
				done();
			}
		},
		after: function(params) {
			// force resize of skews
			resize_skew_div();
		}
	});
   	nlp_router.resolve();

   	function nlpapp_render_tabs(){
   		// reset then render tabs
		var project_tab_ids = ["-step1","-step1","-step2","-step3","-step4"];
		$(".nav-step","#body-application").css("display","none"); // turn off all nav-step tabs
		for (i = 0; i <= nlpapp_dataobject.current_project.progress; i++) {
			$("#mobilenav" + project_tab_ids[i]).show();
			$("#nav" + project_tab_ids[i]).show();
		}
   	}
   	function nlpapp_set_progress_tabs(progress){
   		// iterates progress, already reflected in backend by this point
   		if( progress <= 4){
	   		if ( nlpapp_dataobject.current_project.progress < progress){
	   			nlpapp_dataobject.current_project.progress = progress;
	   		}
	   		// turn off tabs beyond this progress
	   		for(tab=(progress+1);tab<=4;tab++){
		   		$(".nav-tabs li[id='nav-step" + tab +"'], .navbar-nav li[id='mobilenav-step" + tab +"']","#body-application").hide();
		   	}
	   	}
   		//
   	}
   	function nlapp_reset_ui(){
   		// wipes inputs
   		$(".form-feedback,.help-block").removeClass("SUCCESS FIELDLEVEL_ERROR ERROR EXISTS FAIL DENIED MISSING PAYMENT_ERROR").text("").hide();
   		$("input[type=text],textarea").val("");
		$("input:checkbox").removeAttr("checked disabled").removeClass("disabled");
		$("#nlpapp-technologyclasses-table tr").removeClass("disabled");  
   	}
   	// ---------------------------------------------------------------
   	// data setter functions - only 3 of these right now,
   	// but can be added into any hook for step returns functions
   	// ---------------------------------------------------------------
   	function nlpapp_login_setdata(data,callback){
		// currently sets nothing, but leaving hook for later use
		callback();
	}
   	function nlpapp_load_profile_setdata(data,callback){
   		// set profile data to nlpapp_dataobject.user
		nlpapp_dataobject.user.email 			= data.email;
		nlpapp_dataobject.user.first_name		= data.first_name;
		nlpapp_dataobject.user.last_name		= data.last_name;
		nlpapp_dataobject.user.organization	= data.organization;
		nlpapp_dataobject.user.client			= data.client;
		nlpapp_dataobject.user.role			= data.role;
		nlpapp_dataobject.user.admin			= data.admin;
		nlpapp_dataobject.user.country		= data.country;
		nlpapp_dataobject.user.region			= data.region;

		nlpapp_dataobject.user.update_cost		= data.update_cost;
		nlpapp_dataobject.user.search_cost		= data.search_cost;
		nlpapp_dataobject.user.payment_expiry	= data.payment_expiry;
		nlpapp_dataobject.user.payment_number	= data.payment_number;
		nlpapp_dataobject.user.payment_method	= data.payment_method;
		nlpapp_dataobject.user.stripe_key		= data.stripe_key;

		callback();
	}
	function nlpapp_load_currentproject_setdata(data,callback){
		if ( data.name !== null ){
			// set current project data to nlpapp_dataobject.current_project
			// if this is null, the callback dispatches
			nlpapp_dataobject.current_project.name			= data.name;
			nlpapp_dataobject.current_project.last_edited	= data.last_edited;
			nlpapp_dataobject.current_project.progress		= data.progress;
			nlpapp_dataobject.current_project.secure		= data.secure;
			nlpapp_dataobject.security_unlocked 			= 0;
		} else {
			nlpapp_dataobject.current_project.name			= "";
			nlpapp_dataobject.current_project.last_edited	= "";
			nlpapp_dataobject.current_project.progress		= "";
			nlpapp_dataobject.current_project.secure		= "";
			nlpapp_dataobject.security_unlocked 			= 0;
		}
		callback();
	}

   	// ---------------------------------------------------------------
   	// form validations
   	// ---------------------------------------------------------------

	function nlpapp_validate_form_addsavedpriorart(){
		var form = ".addsavedpriorart_group";
		var form_valid = true;
		// validate known prior art
		// ---------------------------------------------------------------
		// regexp's
		var patent_pattern_1 = /^US[0-9]{7}$/;
		var patent_pattern_2 = /^US[0-9]{1},[0-9]{3},[0-9]{3}$/;
		var patent_pattern_3 = /^US[0-9]{8}$/;
		var patent_pattern_4 = /^US[0-9]{2},[0-9]{3},[0-9]{3}$/;
		var patent_pattern_5 = /^US(19|20)\d{2}[0-9]{7}$/;
		var patent_pattern_6 = /^US(19|20)\d{2}\/[0-9]{7}$/;
		var pattern_array =[ patent_pattern_1,patent_pattern_2,patent_pattern_3,patent_pattern_4,patent_pattern_5,patent_pattern_6];

		// validate prior known art (if entered)
		// ---------------------------------------------------------------
		var knownart_error = "Incorrect format. Please try again.";
		var knownart_value = $("#manual_saved_result",form).val();
		if ( knownart_value !== "" ){
			// theve entered a key element so we test it
			switch( knownart_value.toString().length ){
				case 9:
					var knownart_regexp = new RegExp(pattern_array[0]);
					if ( knownart_regexp.test(knownart_value) === false ){
						form_valid = false;
						$("#manual_saved_result",form).siblings(".help-block").text(knownart_error).show();
					} else {
						$("#manual_saved_result",form).siblings(".help-block").text("").hide();
					}
					break;
				case 10:
					var knownart_regexp = new RegExp(pattern_array[2]);
					if ( knownart_regexp.test(knownart_value) === false ){
						form_valid = false;
						$("#manual_saved_result",form).siblings(".help-block").text(knownart_error).show();
					} else {
						$("#manual_saved_result",form).siblings(".help-block").text("").hide();
					}
					break;	
				case 11:
					var knownart_regexp = new RegExp(pattern_array[1]);
					if ( knownart_regexp.test(knownart_value) === false ){
						form_valid = false;
						$("#manual_saved_result",form).siblings(".help-block").text(knownart_error).show();
					} else {
						$("#manual_saved_result",form).siblings(".help-block").text("").hide();
					}
					break;
				case 12:
					var knownart_regexp = new RegExp(pattern_array[3]);
					if ( knownart_regexp.test(knownart_value) === false ){
						form_valid = false;
						$("#manual_saved_result",form).siblings(".help-block").text(knownart_error).show();
					} else {
						$("#manual_saved_result",form).siblings(".help-block").text("").hide();
					}
					break;
				case 13:
					var knownart_regexp = new RegExp(pattern_array[4]);
					if ( knownart_regexp.test(knownart_value) === false ){
						form_valid = false;
						$("#manual_saved_result",form).siblings(".help-block").text(knownart_error).show();
					} else {
						$("#manual_saved_result",form).siblings(".help-block").text("").hide();
					}
					break;
				case 14:
					var knownart_regexp = new RegExp(pattern_array[5]);
					if ( knownart_regexp.test(knownart_value) === false ){
						form_valid = false;
						$("#manual_saved_result",form).siblings(".help-block").text(knownart_error).show();
					} else {
						$("#manual_saved_result",form).siblings(".help-block").text("").hide();
					}
					break;
				default:
					form_valid = false;
					$("#manual_saved_result",form).siblings(".help-block").text(knownart_error).show();					
			}
		}
		return form_valid;
	}

   	function nlpapp_validate_form_stepone(){
   		var stepone_form = "#nlpapp_step_one_form";
   		var stepone_form_valid = true;
   		// regexp's
   		keyelement_regexp = new RegExp("^\\w+(?:\\s+\\w+){0,4}$");
          description_regexp = new RegExp("^[\\s\\S]{150,9999}$");
          // validate description
          // ---------------------------------------------------------------
          var description_error = "Description must be between 150 and 10,000 characters.";
          var description_value = $("#description",stepone_form).val();
          if ( description_value !== ""){
          	if ( description_regexp.test(description_value) ){
          		$("#description",stepone_form).siblings(".help-block").text("").hide();
          	} else {
          		stepone_form_valid = false;
          		$("#description",stepone_form).siblings(".help-block").text(description_error).show();
          	}
          } else {
          	stepone_form_valid = false;
          	$("#description",stepone_form).siblings(".help-block").text(description_error).show();
          }
          // validate key elements (if entered)
          // ---------------------------------------------------------------
          var keyelement_error = "Must be a maximum of 5 words.";
          var keyelement_number = $(".keyelement-field",stepone_form).length;
          for(i=1;i<=keyelement_number;i++){
          	var element_value = $("#element_"+i,stepone_form).val();
          	if ( element_value !== "" ){
          		// theve entered a key element so we test it
          		if ( keyelement_regexp.test(element_value) === false ){
          			stepone_form_valid = false;
          			$("#element_"+i,stepone_form).siblings(".help-block").text(keyelement_error).show();
          		} else {
          			$("#element_"+i,stepone_form).siblings(".help-block").text("").hide();
          		}
          	}
          }
		  // validate known prior art
		  // ---------------------------------------------------------------
			// regexp's
			var patent_pattern_1 = /^US[0-9]{7}$/;
			var patent_pattern_2 = /^US[0-9]{1},[0-9]{3},[0-9]{3}$/;
			var patent_pattern_3 = /^US[0-9]{8}$/;
			var patent_pattern_4 = /^US[0-9]{2},[0-9]{3},[0-9]{3}$/;
			var patent_pattern_5 = /^US(19|20)\d{2}[0-9]{7}$/;
			var patent_pattern_6 = /^US(19|20)\d{2}\/[0-9]{7}$/;
			var pattern_array =[ patent_pattern_1,patent_pattern_2,patent_pattern_3,patent_pattern_4,patent_pattern_5,patent_pattern_6];

			// validate prior known art (if entered)
			// ---------------------------------------------------------------
			var knownart_error = "Incorrect format. Please try again.";
			var knownart_number = $(".knownart-field","#nlpapp_step_one_form").length;
			for(i=1;i<=knownart_number;i++){
				var knownart_value = $("#patent_"+i,"#nlpapp_step_one_form").val();
				if ( knownart_value !== "" ){
					// theve entered a key element so we test it
					switch( knownart_value.toString().length ){
						case 9:
							var knownart_regexp = new RegExp(pattern_array[0]);
							if ( knownart_regexp.test(knownart_value) === false ){
								stepone_form_valid = false;
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text(knownart_error).show();
							} else {
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text("").hide();
							}
							break;
						case 10:
							var knownart_regexp = new RegExp(pattern_array[2]);
							if ( knownart_regexp.test(knownart_value) === false ){
								stepone_form_valid = false;
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text(knownart_error).show();
							} else {
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text("").hide();
							}
							break;	
						case 11:
							var knownart_regexp = new RegExp(pattern_array[1]);
							if ( knownart_regexp.test(knownart_value) === false ){
								stepone_form_valid = false;
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text(knownart_error).show();
							} else {
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text("").hide();
							}
							break;
						case 12:
							var knownart_regexp = new RegExp(pattern_array[3]);
							if ( knownart_regexp.test(knownart_value) === false ){
								stepone_form_valid = false;
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text(knownart_error).show();
							} else {
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text("").hide();
							}
							break;
						case 13:
							var knownart_regexp = new RegExp(pattern_array[4]);
							if ( knownart_regexp.test(knownart_value) === false ){
								stepone_form_valid = false;
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text(knownart_error).show();
							} else {
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text("").hide();
							}
							break;
						case 14:
							var knownart_regexp = new RegExp(pattern_array[5]);
							if ( knownart_regexp.test(knownart_value) === false ){
								stepone_form_valid = false;
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text(knownart_error).show();
							} else {
								$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text("").hide();
							}
							break;
						default:
							stepone_form_valid = false;
							$("#patent_"+i,"#nlpapp_step_one_form").siblings(".help-block").text(knownart_error).show();					
					}
				}
			}
		return stepone_form_valid;
   	}
   	function nlpapp_validate_form_newproject(){
   		var newproject_form = "#nlpapp_new_project";
   		var newproject_form_valid = true;
   		// regexp's
   		newprojectname_regexp = new RegExp("^[\\s\\S]{2,139}$");
          // validate description
          // ---------------------------------------------------------------
          var newproject_error = "Project name must be between 2 and 140 characters.";
          var newproject_value = $("#project_name",newproject_form).val();
          if ( newprojectname_regexp.test(newproject_value) ){
     		$(newproject_form).siblings(".form-feedback").text("");
     	} else {
     		newproject_form_valid = false;
     		$(newproject_form).siblings(".form-feedback").text(newproject_error).show();
     	}
		return newproject_form_valid;
   	}
   	function nlpapp_validate_form_newproject_fromcreate(){
   		var newproject_form = "#nlpapp_new_project_create";
   		var newproject_form_valid = true;
   		// regexp's
   		newprojectname_regexp = new RegExp("^[\\s\\S]{2,139}$");
          // validate description
          // ---------------------------------------------------------------
          var newproject_error = "Project name must be between 2 and 140 characters.";
          var newproject_value = $("#project_name_create",newproject_form).val();
          if ( newprojectname_regexp.test(newproject_value) ){
     		$(newproject_form).siblings(".form-feedback").text("");
     	} else {
     		newproject_form_valid = false;
     		$(newproject_form).siblings(".form-feedback").text(newproject_error).show();
     	}
		return newproject_form_valid;
   	}
   	function nlpapp_validate_form_renameproject(){
   		var newproject_form = "#nlpapp_edit_project_name";
   		var newproject_form_valid = true;
   		// regexp's
   		newprojectname_regexp = new RegExp("^[\\s\\S]{2,139}$");
          // validate description
          // ---------------------------------------------------------------
          var newproject_error = "Project name must be between 2 and 140 characters.";
          var newproject_value = $("#new_name",newproject_form).val();
          if ( newprojectname_regexp.test(newproject_value) ){
     		$("#new_name",newproject_form).siblings(".help-block").text("").hide();
     	} else {
     		newproject_form_valid = false;
     		$("#new_name",newproject_form).siblings(".help-block").text(newproject_error).show();
     	}
		return newproject_form_valid;
   	}
	function nlpapp_validate_form_login(){
   		var login_form = "#nlpapp_login";
   		var login_form_valid = true;
          // validate email
          // ---------------------------------------------------------------
          email_regexp = new RegExp("(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?|\\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-zA-Z0-9-]*[a-zA-Z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])");
          var email_error = "Please enter a valid email.";
          var email_value = $("#email",login_form).val();
          if ( email_value !== ""){
          	if ( email_regexp.test(email_value) ){
          		$("#email",login_form).siblings(".help-block").text("").hide();
          	} else {
          		login_form_valid = false;
          		$("#email",login_form).siblings(".help-block").text(email_error).show();
          	}
          } else {
          	login_form_valid = false;
          	$("#email",login_form).siblings(".help-block").text(email_error).show();
          }
          // validate password
          // ---------------------------------------------------------------
          var password_error = "Please enter your password.";
          var password_value = $("#password",login_form).val();
          if ( password_value == ""){
          	login_form_valid = false;
          	$("#password",login_form).siblings(".help-block").text(password_error).show();
          } else {
          	$("#password",login_form).siblings(".help-block").text(password_error).hide();
          }
		return login_form_valid;
   	}
   	function nlpapp_validate_form_unlockstep1(){
   		var unlockstep1_form = "#nlpapp_step1_unlock";
   		var unlockstep1_form_valid = true;
          // validate password
          // ---------------------------------------------------------------
          var unlockstep1_error = "Please enter your password.";
          var unlockstep1_value = $("#unlock_password",unlockstep1_form).val();
          if ( unlockstep1_value !== "" ){
     		$("#unlock_password",unlockstep1_form).siblings(".help-block").text("").hide();
     	} else {
     		newproject_form_valid = false;
     		$("#unlock_password",unlockstep1_form).siblings(".help-block").text(unlockstep1_error).show();
     	}
		return unlockstep1_form_valid;
   	}
   	function nlpapp_validate_form_forgotpassword(){
   		var login_form = "#nlpapp_forgotpassword";
   		var login_form_valid = true;
          // validate email
          // ---------------------------------------------------------------
          email_regexp = new RegExp("(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])");
          var email_error = "Please enter a valid email.";
          var email_value = $("#forgotpassword_email",login_form).val();
          if ( email_value !== ""){
          	if ( email_regexp.test(email_value) ){
          		$("#forgotpassword_email",login_form).siblings(".help-block").text("").hide();
          	} else {
          		login_form_valid = false;
          		$("#forgotpassword_email",login_form).siblings(".help-block").text(email_error).show();
          	}
          } else {
          	login_form_valid = false;
          	$("#forgotpassword_email",login_form).siblings(".help-block").text(email_error).show();
          }
		return login_form_valid;
   	}
   	function nlpapp_validate_form_signup(){
   		var login_form = "#nlpapp_signup";
   		var login_form_valid = true;
          // validate email
          // ---------------------------------------------------------------
          email_regexp = new RegExp("(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])");
          var email_error = "Please enter a valid email.";
          var email_value = $("#signup_email",login_form).val();
          if ( email_value !== ""){
          	if ( email_regexp.test(email_value) ){
          		$("#signup_email",login_form).siblings(".help-block").text("").hide();
          	} else {
          		login_form_valid = false;
          		$("#signup_email",login_form).siblings(".help-block").text(email_error).show();
          	}
          } else {
          	login_form_valid = false;
          	$("#signup_email",login_form).siblings(".help-block").text(email_error).show();
          }
          // validate name
          // ---------------------------------------------------------------
          name_regexp = new RegExp("^[\\s\\S]{2,}$");
          var name_error = "Please enter your name, minimum of 2 characters.";
          var name_value = $("#signup_name",login_form).val();
          if ( name_value !== ""){
          	if ( name_regexp.test(name_value) ){
          		$("#signup_name",login_form).siblings(".help-block").text("").hide();
          	} else {
          		login_form_valid = false;
          		$("#signup_name",login_form).siblings(".help-block").text(name_error).show();
          	}
          } else {
          	login_form_valid = false;
          	$("#signup_name",login_form).siblings(".help-block").text(name_error).show();
          }
		return login_form_valid;
   	}
   	function nlpapp_validate_form_changeprofile(){
   		var changeprofile_form = "#nlpapp_edit_profile";
   		var changeprofile_form_valid = true;
          // validate first name
          // ---------------------------------------------------------------
          firstname_regexp = new RegExp("^[\\s\\S]{2,}$");
          var firstname_error = "Please enter your name, minimum of 2 characters.";
          var firstname_value = $("#profile_first_name",changeprofile_form).val();
          if ( firstname_value !== ""){
          	if ( firstname_regexp.test(firstname_value) ){
          		$("#profile_first_name",changeprofile_form).siblings(".help-block").text("").hide();
          	} else {
          		changeprofile_form_valid = false;
          		$("#profile_first_name",changeprofile_form).siblings(".help-block").text(firstname_error).show();
          	}
          } else { // only for first name - should never be ""
				changeprofile_form_valid = false;
        		$("#profile_first_name",changeprofile_form).siblings(".help-block").text(firstname_error).show();
		  }
          // validate last name
          // ---------------------------------------------------------------
          lastname_regexp = new RegExp("^[\\s\\S]{1,}$");
          var lastname_error = "Please enter your name, minimum of 1 character.";
          var lastname_value = $("#profile_last_name",changeprofile_form).val();
          if ( lastname_value !== ""){
          	if ( lastname_regexp.test(lastname_value) ){
          		$("#profile_last_name",changeprofile_form).siblings(".help-block").text("").hide();
          	} else {
          		changeprofile_form_valid = false;
          		$("#profile_last_name",changeprofile_form).siblings(".help-block").text(lastname_error).show();
          	}
          }
          // validate last name
          // ---------------------------------------------------------------
          role_regexp = new RegExp("^[\\s\\S]{2,}$");
          var role_error = "Please enter your name, minimum of 2 characters.";
          var role_value = $("#profile_role",changeprofile_form).val();
          if ( role_value !== ""){
          	if ( role_regexp.test(role_value) ){
          		$("#profile_role",changeprofile_form).siblings(".help-block").text("").hide();
          	} else {
          		changeprofile_form_valid = false;
          		$("#profile_role",changeprofile_form).siblings(".help-block").text(role_error).show();
          	}
          }
		return changeprofile_form_valid;
   	}
   	function nlpapp_validate_form_changepassword(){
   		var changepassword_form = "#nlpapp_change_password";
   		var changepassword_form_valid = true;
          // validate current password
          // ---------------------------------------------------------------
          var changepassword_error = "Please enter your current password.";
          var changepassword_value = $("#profile_current_password",changepassword_form).val();
          if ( changepassword_value !== ""){
          	$("#profile_current_password",changepassword_form).siblings(".help-block").text("").hide();
          } else {
          	changepassword_form_valid = false;
          	$("#profile_current_password",changepassword_form).siblings(".help-block").text(changepassword_error).show();
          }
          // validate new password
          // ---------------------------------------------------------------
          newpassword_regexp = new RegExp("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{6,}$");
          var newpassword_error = "Password must be at least 6 characters, and at least 1 number and uppercase letter.";
          var newpassword_value = $("#profile_new_password",changepassword_form).val();
          if ( newpassword_value !== ""){
          	if ( newpassword_regexp.test(newpassword_value) ){
          		$("#profile_new_password",changepassword_form).siblings(".help-block").text("").hide();
          	} else {
          		changepassword_form_valid = false;
          		$("#profile_new_password",changepassword_form).siblings(".help-block").text(newpassword_error).show();
          	}
          } else {
          	changepassword_form_valid = false;
          	$("#profile_new_password",changepassword_form).siblings(".help-block").text(newpassword_error).show();
          }
          // validate confirm new password
          // ---------------------------------------------------------------
          var confirmnewpassword_error = "Passwords must match.";
          var confirmnewpassword_value = $("#profile_confirmnew_password",changepassword_form).val();
          if ( confirmnewpassword_value !== ""){
          	if ( $("#profile_new_password").val() == confirmnewpassword_value){
          		$("#profile_confirmnew_password",changepassword_form).siblings(".help-block").text("").hide();
          	} else {
          		changepassword_form_valid = false;
          		$("#profile_confirmnew_password",changepassword_form).siblings(".help-block").text(confirmnewpassword_error).show();
          	}
          } else {
          	changepassword_form_valid = false;
          	$("#profile_confirmnew_password",changepassword_form).siblings(".help-block").text(confirmnewpassword_error).show();
          }
		return changepassword_form_valid;
   	}
   	function nlpapp_validate_form_resetpassword(){
   		var resetpassword_form = "#nlpapp_resetpassword";
   		var resetpassword_form_valid = true;
          // validate new password
          // ---------------------------------------------------------------
          newpassword_regexp = new RegExp("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{6,}$");
          var newpassword_error = "Password must be at least 6 characters, and at least 1 number and uppercase letter.";
          var newpassword_value = $("#reset_password",resetpassword_form).val();
          if ( newpassword_value !== ""){
          	if ( newpassword_regexp.test(newpassword_value) ){
          		$("#reset_password",resetpassword_form).siblings(".help-block").text("").hide();
          	} else {
          		resetpassword_form_valid = false;
          		$("#reset_password",resetpassword_form).siblings(".help-block").text(newpassword_error).show();
          	}
          } else {
          	resetpassword_form_valid = false;
          	$("#reset_password",resetpassword_form).siblings(".help-block").text(newpassword_error).show();
          }
          // validate confirm new password
          // ---------------------------------------------------------------
          var confirmnewpassword_error = "Passwords must match.";
          var confirmnewpassword_value = $("#confirm_reset_password",resetpassword_form).val();
          if ( confirmnewpassword_value !== ""){
          	if ( $("#reset_password").val() == confirmnewpassword_value){
          		$("#confirm_reset_password",resetpassword_form).siblings(".help-block").text("").hide();
          	} else {
          		resetpassword_form_valid = false;
          		$("#confirm_reset_password",resetpassword_form).siblings(".help-block").text(confirmnewpassword_error).show();
          	}
          } else {
          	resetpassword_form_valid = false;
          	$("#confirm_reset_password",resetpassword_form).siblings(".help-block").text(confirmnewpassword_error).show();
          }
		return resetpassword_form_valid;
   	}
   	function nlpapp_validate_form_changecap(currentusage){
   		var changecap_form = "#nlpapp_change_usagecap";
   		var changecap_form_valid = true;
          // validate cap amount
          // ---------------------------------------------------------------
          var changecap_error = "Must be a number, and not less than current usage of $" + currentusage +".";
          var changecap_value = $("#change_cap",changecap_form).val();
          if ( $.isNumeric(changecap_value) && Math.floor(changecap_value) == changecap_value){
     		$("#change_cap",changecap_form).siblings(".help-block").text("").hide();
     	} else {
     		changecap_form_valid = false;
     		$("#change_cap",changecap_form).siblings(".help-block").text(changecap_error).show();
     	}
		return changecap_form_valid;
   	}
});