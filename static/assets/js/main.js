/*
	Read Only by Pixelarity
	pixelarity.com @pixelarity
	License: pixelarity.com/license
*/

(function($) {

	skel.breakpoints({
		xlarge: '(max-width: 1680px)',
		large: '(max-width: 1280px)',
		medium: '(max-width: 1024px)',
		small: '(max-width: 736px)',
		xsmall: '(max-width: 480px)'
	});

	$(function() {

		var $body = $('body'),
			$header = $('#header'),
			$nav = $('#nav'), $nav_a = $nav.find('a'),
			$wrapper = $('#wrapper');

		// Fix: Placeholder polyfill.
			$('form').placeholder();

		// Prioritize "important" elements on medium.
			skel.on('+medium -medium', function() {
				$.prioritize(
					'.important\\28 medium\\29',
					skel.breakpoint('medium').active
				);
			});

		// Header.
			var ids = [];

			// Set up nav items.
				$nav_a
					.scrolly({ offset: 44 })
					.on('click', function(event) {

						var $this = $(this),
							href = $this.attr('href');

						// Not an internal link? Bail.
							if (href.charAt(0) != '#')
								return;

						// Prevent default behavior.
							event.preventDefault();

						// Remove active class from all links and mark them as
						// locked (so scrollzer leaves them alone).
							$nav_a
								.removeClass('active')
								.addClass('scrollzer-locked');

						// Set active class on this link.
							$this.addClass('active');

					})
					.each(function() {

						var $this = $(this),
							href = $this.attr('href'),
							id;

						// Not an internal link? Bail.
							if (href.charAt(0) != '#')
								return;

						// Add to scrollzer ID list.
							id = href.substring(1);
							$this.attr('id', id + '-link');
							ids.push(id);

					});

			// Initialize scrollzer.
				$.scrollzer(ids, { pad: 300, lastHack: true });

		// Off-Canvas Navigation.

			// Title Bar.
				$(
					'<div id="titleBar">' +
						'<a href="#header" class="toggle"></a>' +
						'<span class="title">' + $('#logo').html() + '</span>' +
					'</div>'
				)
					.appendTo($body);

			// Header.
				$('#header')
					.panel({
						delay: 500,
						hideOnClick: true,
						hideOnSwipe: true,
						resetScroll: true,
						resetForms: true,
						side: 'right',
						target: $body,
						visibleClass: 'header-visible'
					});

			// Fix: Remove navPanel transitions on WP<10 (poor/buggy performance).
				if (skel.vars.os == 'wp' && skel.vars.osVersion < 10)
					$('#titleBar, #header, #wrapper')
						.css('transition', 'none');

				// query index to keep track of number of queries
				var queryID = 1;
				var secondQueryRemoved = false;
				var thirdQueryRemoved = false;
				var fourthQueryRemoved = false;
				var fifthQueryRemoved = false;
				var querySecondaryID = 1;
				var secondQuerySecondaryRemoved = false;
				var thirdQuerySecondaryRemoved = false;
				var fourthQuerySecondaryRemoved = false;
				var fifthQuerySecondaryRemoved = false;
				var clickBtnSearch = true;
				var clickBtnNewSearch = true;

				/* jquery code to add multiple field inputs.*/
				$(".addQuery").on('click', function(event) {
					if (queryID < 5) {
						if (secondQueryRemoved) {queryID = 2;}
						else if (thirdQueryRemoved) {queryID = 3;}
						else if (fourthQueryRemoved) {queryID = 4;}
						else if (fifthQueryRemoved) {queryID = 5;}
						else {queryID++;}

				        var elementNameID = "query" + queryID.toString();

						$(".additionalInputField").before(
							'<div class="queryField" id="' + elementNameID + '">' +
								'<input type="text" name="' + elementNameID + '" placeholder="" />' +
								'<div class="btnGroup">' +
									'<button class="removeQuery" type="button">' +
										'<i class="fa fa-minus fa-2x" aria-hidden="true"></i>' +
									'</button>' +
								'</div>' +
							'</div>'
						);

						secondQueryRemoved = false;
						thirdQueryRemoved = false;
						fourthQueryRemoved = false;
						fifthQueryRemoved = false;
					}
			    });

				/* jquery code to remove an input field */
				$("body").on('click', 'button.removeQuery', function(event) {
					if (queryID >= 1) {
						var elementToRemove = $(this).parent().parent();
						$(this).parent().parent().remove();
						queryID--;
						if (elementToRemove.attr('id') == 'query2') {
							secondQueryRemoved = true;
						} else if (elementToRemove.attr('id') == 'query3') {
							thirdQueryRemoved = true;
						} else if (elementToRemove.attr('id') == 'query4') {
							fourthQueryRemoved = true;
						} else if (elementToRemove.attr('id') == 'query5') {
							fifthQueryRemoved = true;
						}
			        }
				});

				/* jquery code to add multiple field inputs.*/
				$(".addQuerySecondary").on('click', function(event) {
					if (querySecondaryID < 5) {
						if (secondQuerySecondaryRemoved) {querySecondaryID = 2;}
						else if (thirdQuerySecondaryRemoved) {querySecondaryID = 3;}
						else if (fourthQuerySecondaryRemoved) {querySecondaryID = 4;}
						else if (fifthQuerySecondaryRemoved) {querySecondaryID = 5;}
						else {querySecondaryID++;}

				        var elementNameSecondaryID = "querySecondary" + querySecondaryID.toString();

						$(".additionalInputFieldSecondary").before(
							'<div class="queryField" id="' + elementNameSecondaryID + '">' +
								'<input type="text" name="' + elementNameSecondaryID + '" placeholder="" />' +
								'<div class="btnGroup">' +
									'<button class="removeQuerySecondary" type="button">' +
										'<i class="fa fa-minus fa-2x" aria-hidden="true"></i>' +
									'</button>' +
								'</div>' +
							'</div>'
						);

						secondQuerySecondaryRemoved = false;
						thirdQuerySecondaryRemoved = false;
						fourthQuerySecondaryRemoved = false;
						fifthQuerySecondaryRemoved = false;
					}
			    });

				/* jquery code to remove an input field */
				$("body").on('click', 'button.removeQuerySecondary', function(event) {
					if (querySecondaryID >= 1) {
						var elementToRemoveSecondary = $(this).parent().parent();
						$(this).parent().parent().remove();
						querySecondaryID--;
						if (elementToRemoveSecondary.attr('id') == 'querySecondary2') {
							secondQuerySecondaryRemoved = true;
						} else if (elementToRemoveSecondary.attr('id') == 'querySecondary3') {
							thirdQuerySecondaryRemoved = true;
						} else if (elementToRemoveSecondary.attr('id') == 'querySecondary4') {
							fourthQuerySecondaryRemoved = true;
						} else if (elementToRemoveSecondary.attr('id') == 'querySecondary5') {
							fifthQuerySecondaryRemoved = true;
						}
			        }
				});

				/* functionlity to submit form on 'enter' key */
				$(".enterQuery").on('keydown', function(event) {
					// event.preventDefault();
					/* Act on the event */
					if (event.keyCode == 13) {
						$("#searchForm").submit();
					}
				});

				/* jquery code to add loading animation */
				$("#btnSearch").on('click', function() {
					if (clickBtnSearch) {
						$("#btnSearch").after(
							'&nbsp&nbsp<i class="fa fa-spinner fa-pulse fa-lg fa-fw"></i>' +
							'&nbsp&nbsp&nbsp' +
							'Processing...'
						);
						$("#btnSearch").attr("disabled", true);
						$("#btnSearch").parents('form').submit();
					}
					clickBtnSearch = false;
				});

			    /* jquery code to add loading animation to new search button */
				$("#btnNewSearch").on('click', function() {
					if (clickBtnNewSearch) {
						$("#btnNewSearch").after(
							'&nbsp&nbsp<i class="fa fa-spinner fa-pulse fa-lg fa-fw"></i>' +
							'&nbsp&nbsp&nbsp' +
							'Searching for prior art...'
						);
						$("#btnNewSearch").attr("disabled", true);
						$("#btnNewSearch").parents('form').submit();
					}
					clickBtnNewSearch = false;
				});

				/* Add functionality to toggle dropdown menu */
				$(".dropLink").on('contextmenu', function(event) {
			        event.preventDefault();
			        $('.dropdown-content').hide();
			        var rowClicked = '#' + $(this).parent().parent().parent().attr('id');
			        var rowClickedDropdownMenu = $(rowClicked).children('.caseLink').children('div').children('.dropdown-content');
			        rowClickedDropdownMenu.show();
			    });

			    $("body").on('click', function() {
			        $('.dropdown-content').hide();
			    });

			    $(".addToProject").on('click', function(event) {
			        event.preventDefault();

			        var rowClicked = '#' + $(this).parent().parent().parent().parent().attr('id');
					var caseNameDiv = $(rowClicked).children('.caseName').children('div');
					var caseDropLink = $(rowClicked).children('.caseLink').children('div').children('.dropLink');

			        var objectToSend = {
			            projectTitle: $(this).text().trim(),
			            caseName: caseNameDiv.text().trim(),
			            caseLink: caseDropLink.attr("href"),
			            caseCitation: caseDropLink.text().trim()
			        };

					$.ajax({
						url: '/savecase',
						type: 'POST',
						dataType: 'json',
						data: objectToSend
					})
					.done(function(data) {
						$('.dropdown-content').hide();
						toastr.options = {
                            "closeButton": true,
                            "debug": false,
                            "newestOnTop": false,
                            "progressBar": false,
                            "positionClass": "toast-top-right",
                            "preventDuplicates": false,
                            "onclick": null,
                            "showDuration": "300",
                            "hideDuration": "1000",
                            "timeOut": "2500",
                            "extendedTimeOut": "1000",
                            "showEasing": "swing",
                            "hideEasing": "linear",
                            "showMethod": "fadeIn",
                            "hideMethod": "fadeOut"
                        }
                        if(data.case) {
                            toastr.success(data.case, 'Successfully added:');
                        } else if(data.project) {
                            toastr.warning(data.project, 'Already added to project:');
                        }
						console.log("success");
						console.log(data);
					})
					.fail(function(data) {
						$('.dropdown-content').hide();
						console.log("error");
						console.log(data);
					});

			    });

				/* Functionality for accordion */
				$("#accordion")
			        .accordion({
			            header: "> div > h3",
			            collapsible: true,
			            active: false,
						heightStyle: "content"
			        })
			        .sortable({
			            axis: "y",
			            handle: "h3",
						start: function(event, ui) {
							// creates a temporary attribute on the element with the old index
							$(this).attr('data-previndex', ui.item.index());
						},
						update: function(event, ui) {
							var newIndex = ui.item.index();

							// var caseId = '#' + ui.item.attr('id');
							var projectTitle = $('#titleWrapper').children('#projectTitle').text();

					        var oldIndex = $(this).attr('data-previndex');
					        $(this).removeAttr('data-previndex');

							var dataObject = {
			                    new_index: newIndex,
			                    old_index: oldIndex,
								project_title: projectTitle
			                };

							$.ajax({
								url: '/rearrangecases',
								type: 'POST',
								dataType: 'json',
								data: dataObject
							})
							.done(function(data) {
								console.log("success");
							})
							.fail(function(xhr, err) {
								console.log("error");
								console.log(xhr.responseText);
								console.log(err);
							})
							.always(function() {
								console.log("complete");
							});

						},
			            stop: function(event, ui) {
			                ui.item.children('h3').triggerHandler('focusout');
			                $(this).accordion("refresh");
			            }
			        });

				/* Functionality to edit titles. */

				// Grab old title on load.
				var oldTitle = $("#projectTitle").text();
				// Flag to ensure multiple save and cancel buttons aren't added
				var clickProjectTitle = true;

				// function to remove buttons and event handlers.
				function removeButtons() {
					// Removing buttons and event handlers for buttons.
					$("body")
						.off('click', '#changeTitleSubmit', saveChanges)
						.find('#changeTitleSubmit').remove();
					$("body")
						.off('click', '#changeTitleCancel', removeButtons)
						.find('#changeTitleCancel').remove();
					$("#changeTitleBtnGroup").remove();
					// Toggle flag
					clickProjectTitle = true;
				}

				// function to save changes to title.
				function saveChanges() {
					// Capture changes made to projectTitle.
					var newTitle = $("#projectTitle").text();

					// store old and new titles inside data object
					var dataObject = {
						old_title: oldTitle,
						new_title: newTitle
					};

					// makes ajax request to complete changes.
					$.ajax({
						url: '/changetitle',
						type: 'POST',
						dataType: 'json',
						data: dataObject
					})
					.done(function(data) {
						$("#projectTitle").text(newTitle);
						$("#projectTitleForWord").val(newTitle);
						oldTitle = newTitle;
					})
					.fail(function(xhr, err) {
						$("#projectTitle").text(oldTitle);
					})
					.always(function() {
						removeButtons();
					});
				}

				// function to cancel changes to title.
				function cancelChanges() {
					$("#projectTitle").text(oldTitle);
					removeButtons();
				}

				// function to add buttons upon clicking project titles.
				$("body").on('click', '#projectTitle', function() {
					// Gets project title before any title wrapper is replaced
					var projectTitle = $(this).text();

					// Adds buttons after project title.
					if (clickProjectTitle) {
						$(this).after(
							'<span id="changeTitleBtnGroup">' +
							'<input id="changeTitleSubmit" type="submit"' +
							' value="Save change" class="alt small" />' +
							'&nbsp;&nbsp;' +
							'<input id="changeTitleCancel" type="submit" ' +
							'value="Cancel" class="alt small" />' +
							'</span>'
						);

						// Event handler for clicking 'Save Changes button'.
						$('#changeTitleSubmit').on('click', saveChanges);
						// Event handler for clicking 'Cancel Changes button'.
						$('#changeTitleCancel').on('click', cancelChanges);
					}

					// Toggle flag
					clickProjectTitle = false;
				});

				/* Functionality to edit notes*/

				$("body").on('click', '.editable-notes', function() {
			        var caseId = '#' + $(this).parent('.caseArea').parent().attr('id');
			        var notesToEdit = $(caseId).children('.caseArea').children('.editable-notes');
			        var editingNotesForm = $(caseId).children('.caseArea').children('.editingNotesForm');
					var caseNoteMarkdown = $(caseId).children('.caseArea').children('.caseNoteMarkdown');
			        var oldNotes = caseNoteMarkdown.text();
			        notesToEdit.hide();
			        editingNotesForm.show();
			        editingNotesForm.children('textarea').val(oldNotes);
			    });

			    function saveNotesChanges() {
			        var caseId = '#' + $(this).parent('.editingNotesBtnGroup').parent('.editingNotesForm').parent('.caseArea').parent().attr('id');
			        var notesToEdit = $(caseId).children('.caseArea').children('.editable-notes');
			        var editingNotesForm = $(caseId).children('.caseArea').children('.editingNotesForm');
					var editingNotesFormVal = editingNotesForm.children('textarea').val();
			        var caseNoteMarkdown = $(caseId).children('.caseArea').children('.caseNoteMarkdown');
			        var caseHeader = $(caseId).children('h3').text().split(', ');
			        var caseName = caseHeader[0];
			        var caseCitation = caseHeader[1];
					var projectTitle = $("#projectTitle").text();

			        var dataObject = {
			            new_text: editingNotesFormVal,
			            case_name: caseName,
			            case_citation: caseCitation,
						project_title: projectTitle
			        };

					$.ajax({
						url: '/savenote',
						type: 'POST',
						dataType: 'json',
						data: dataObject
					})
					.done(function(data) {
				        // var editingNotesFormVal = editingNotesForm.children('textarea').val();
						caseNoteMarkdown.text(data.markdown);
				        notesToEdit.html(data.html);
					})
					.fail(function(xhr, err) {
						console.log("error");
						console.log(xhr.responseText);
						console.log(err);
					})
					.always(function() {
				        $(".editingNotesForm").hide();
				        $(".editable-notes").show();
					});
			    }

			    function replaceFormWithNotes() {
			        var caseId = '#' + $(this).parent('.caseArea').parent().attr('id');
			        var notesToEdit = $(caseId).children('.caseArea').children('.editable-notes');
			        $(".editingNotesForm").hide();
			        $(".editable-notes").show();
			    }

				function closeAllForms() {
					$(".editingNotesForm").hide();
					$(".caseDeletionForm").hide();
					$(".editable-notes").show();
				}

			    $(".markdownBtn").click(function() {
			        var caseId = '#' + $(this).parent('.markdownBtnGroup').parent('.editingNotesForm').parent('.caseArea').parent().attr('id');
			        var editingNotesFormTextArea = $(caseId).children('.caseArea').children('.editingNotesForm').children('textarea');
			        var command = $(this).attr('id');

			        if (command === 'boldBtn') {editingNotesFormTextArea.mdBold();}
			        if (command === 'italicBtn') {editingNotesFormTextArea.mdItalic();}
			        if (command === 'header1Btn') {editingNotesFormTextArea.mdHeader({number: 1});}
			        if (command === 'header2Btn') {editingNotesFormTextArea.mdHeader({number: 2});}
			        if (command === 'header3Btn') {editingNotesFormTextArea.mdHeader({number: 3});}
			        if (command === 'header4Btn') {editingNotesFormTextArea.mdHeader({number: 4});}
			        if (command === 'linkBtn') {editingNotesFormTextArea.mdLink({default_url: 'http://www.google.com'});}
			        if (command === 'imageBtn') {editingNotesFormTextArea.mdImage({default_image_url: 'Enter URL Please'});}
			        if (command === 'quoteBtn') {editingNotesFormTextArea.mdQuote();}
			        if (command === 'codeBtn') {editingNotesFormTextArea.mdCode();}
			        if (command === 'numberedListBtn') {editingNotesFormTextArea.mdNumberedList();}
			        if (command === 'bulletListBtn') {editingNotesFormTextArea.mdBulletList();}
			    });

			    $(".changeNotesSubmit").on('click', saveNotesChanges);
			    $(".changeNotesCancel").on('click', replaceFormWithNotes);
			    $(".caseTitle").on('click', closeAllForms);

				/* Functionality to delete entry */

				// Hide .no-cases paragraph if
				// there are no cases
				if ($("#accordion").children().length >= 1) {
					$(".no-cases").hide();
				}

				// Event handler for .deleteCase button
				$(".deleteCase").on('click', function() {
					// Opens delete case form
					$(".caseDeletionForm").show();
				});

				// Event handler for #cancelBtn button
				$(".cancelBtn").on('click', function() {
					// Hides delete case form
					$(".caseDeletionForm").hide();
				});

				// Event handler for #deleteCaseBtn button
				$(".deleteCaseBtn").on('click', function() {
					// Retrieve project title
					var projectTitle = $('#titleWrapper').children('#projectTitle').text();
					// Retrieve Case Id from #deleteCaseBtn clicked
					var caseId = '#' + $(this).parent('.deleteCaseBtnGroup').parent().parent('.caseArea').parent().attr('id');
					// Retrieve case name and case header using caseId
					var caseHeader = $(caseId).children('h3').text().split(', ');
					var caseName = caseHeader[0];
					var caseCitation = caseHeader[1];

					// Create dataObject to pass into AJAX request
					var dataObject = {
						project_title: projectTitle,
						case_name: caseName,
						case_citation: caseCitation
					};

					// Make AJAX request to /deletecase
					$.ajax({
						url: '/deletecase',
						type: 'POST',
						dataType: 'json',
						data: dataObject
					})
					.done(function(data) {
						$(caseId).remove();
					})
					.fail(function(xhr, err) {
						console.log("error");
						console.log(xhr.responseText);
						console.log(err);
					})
					.always(function() {
						$(".caseDeletionForm").hide();
						if ($("#accordion").children().length < 1) {
							$(".no-cases").show();
						}
					});
				});

				/* Remove project deletion form */

				// Event handler for clicking 'Delete project'
				$(".openDeletion").on('click', function() {
					$nav_a
						.removeClass('active')
						.addClass('scrollzer-locked');
					$(".deletionForm").hide();
					$("#projectDeletionForm").show();
				});

				// Event handler for removing project deletion form
				$("#cancelProjectDeletion").on('click', function() {
					$("a#-link").removeClass('active');
					$("#projectDeletionForm").hide();
				});

				/* Event handler for save to word file */

				// Open confirmation on clicking .saveWord
				$(".saveWord").on('click', function() {
					// var projectTitle = $("#projectTitle").text();
					//
					// $nav_a
					// 	.removeClass('active')
					// 	.addClass('scrollzer-locked');
					//
					// $.ajax({
					// 	url: '/saveword',
					// 	type: 'POST',
					// 	data: {project_title: projectTitle}
					// })
					// .done(function() {
					// 	console.log("success");
					// })
					// .fail(function() {
					// 	console.log("error");
					// })
					// .always(function() {
					// 	console.log("complete");
					// });
					$nav_a
						.removeClass('active')
						.addClass('scrollzer-locked');
					$(".deletionForm").hide();
					$("#saveWordConfirmation").show();
				});

				// Hide form on clicking #cancelSave
				$("#cancelSave").on('click', function(event) {
					event.preventDefault();
					$("#saveWordConfirmation").hide();
				});

				$("#saveWordForm").submit(function(event) {
					$("#saveWordConfirmation").hide();
				});
	});

})(jQuery);
