/** SPELLING **/
let spBtnClicked = 1
  function spellCheck() {
    const textElement = document.getElementById("assignment-text-body")
    let textElementHTML = textElement.innerHTML
    const originalText = textElement.innerText
    const wordCount = originalText.match(/(\w+)/g).length;
    $.ajax({
            url: location.origin + "/grading-comparison",
            type: 'POST',
            data: JSON.stringify({
                "original_text": originalText
            }),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
              var highlightedText = response.spell_check_result;
              var mistakesCount = response.spell_check_mistakes;

              textElement.innerHTML = highlightedText;

              if (spBtnClicked == 1) {
                document.getElementById("metrics-spelling").innerHTML = 
                              "<span style='font-weight:bold; font-size: 25px;'>Spelling: </span> "+
                              (100 - mistakesCount/wordCount*100).toFixed(2) + '%.'                           
                spBtnClicked = 0
              } else {
                textElement.innerHTML = originalText 
                spBtnClicked = 1
              }
            },
            error: function (response) {
              alert("Error!")
            }
        });
    }

/** GRAMMAR **/
let grBtnClicked = 1
  function grammarCheck(){
    const textElement = document.getElementById("assignment-text-body")
    const originalText = textElement.innerText
    const sentCount = originalText.match(/[\w|\)][.?!](\s|$)/g).length;
    var innerHTMLContent = "";
    $.ajax({
            url: location.origin + "/grading-comparison",
            type: 'POST',
            data: JSON.stringify({
                "original_text": originalText
            }),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
                    var results = response.grammar_check_results; //array
                    function hightlightGrammarlyIncorrectSentences() {
                      var faults = 0;
                      var sentence; var index;
                      for(var i in results) {
                        sentence = results[i][0]
                        index = results[i][1]
                        if(index == 0) {//grammarly incorrect
                          innerHTMLContent = innerHTMLContent + '<u style="text-decoration-color: red;">'+sentence+'</u>. '
                          faults += 1;
                        } else {
                          innerHTMLContent = innerHTMLContent + sentence + '. '
                        }
                      }
                      textElement.innerHTML = innerHTMLContent; 
                      return faults;
                    }

                    if (grBtnClicked == 1) {
                      const faults = hightlightGrammarlyIncorrectSentences()
                      document.getElementById("metrics-grammar").innerHTML = 
                                    "<span style='font-weight:bold; font-size: 25px;'>Grammar: </span> "+
                                    (100 - faults/sentCount*100).toFixed(2) + '%.' 
                      grBtnClicked = 0
                    } else {
                      textElement.innerHTML = originalText;
                      grBtnClicked = 1
                    }
            },
            error: function (response) {
              alert("Error!")
            }
        });
  }
  
/** ARGUMENTATION **/
let argBtnClicked = 1;
  function argCheck(){
    const textElement = document.getElementById("assignment-text-body")
    const originalText = textElement.innerText;
    var innerHTMLContent = "";
    $.ajax({
            url: location.origin + "/grading-comparison",
            type: 'POST',
            data: JSON.stringify({
                "original_text": originalText
            }),
            contentType: "application/json",
            dataType: "json",
            success: function (response) {
                    var predictions = response.predictions; //array
                    var pred;
                    function hightlightClaimsAndPremises() {
                      var claims = 0; var premises = 0;
                        for (var i in predictions){
                          pred = predictions[i]
                          if (pred['label'] == "PREMISE") {
                            innerHTMLContent = innerHTMLContent + '<mark style="background-color: orange;">'+pred['sentence']+'</mark>. '
                            premises += 1
                          } else if (pred['label'] == 'CLAIM') {
                            innerHTMLContent = innerHTMLContent + '<mark style="background-color: yellow;">'+pred['sentence']+'</mark>. '
                            claims += 1
                          }
                        }
                      textElement.innerHTML = innerHTMLContent;

                      return [claims, premises]
                    }

                    if (argBtnClicked == 1) {
                      const r = hightlightClaimsAndPremises()
                      const claims = r[0]; const premises = r[1];
                      document.getElementById("metrics-argumentation").innerHTML = 
                                    "<span style='font-weight:bold; font-size: 25px;'>Argumentation: </span> "+
                                    premises + ' premises and ' + claims + ' claims.' 
                      argBtnClicked = 0
                    } else {
                      textElement.innerHTML = originalText;
                      argBtnClicked = 1
                    }
            },
            error: function (response) {
              alert("Error!")
            }
        });
  }