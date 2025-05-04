(function($) {
    "use strict"

    // Create a dummy Datamap object if it doesn't exist to prevent errors
    if (typeof Datamap === 'undefined') {
        window.Datamap = function() {
            console.warn('Datamap library not loaded - using dummy implementation');
            return {
                bubbles: function() { return this; },
                resize: function() { return this; }
            };
        };
    }

    //todo list
    $(".tdl-new").on('keypress', function(e) {

        var code = (e.keyCode ? e.keyCode : e.which);

        if (code == 13) {

            var v = $(this).val();

            var s = v.replace(/ +?/g, '');

            if (s == "") {

                return false;

            } else {

                $(".tdl-content ul").append("<li><label><input type='checkbox'><i></i><span>" + v + "</span><a href='#' class='ti-trash'></a></label></li>");

                $(this).val("");

            }

        }

    });





    $(".tdl-content a").on("click", function() {

        var _li = $(this).parent().parent("li");

        _li.addClass("remove").stop().delay(100).slideUp("fast", function() {

            _li.remove();

        });

        return false;

    });



    // for dynamically created a tags

    $(".tdl-content").on('click', "a", function() {

        var _li = $(this).parent().parent("li");

        _li.addClass("remove").stop().delay(100).slideUp("fast", function() {

            _li.remove();

        });

        return false;

    });








})(jQuery);


(function($) {
    "use strict"

    // Datamaps initialization with null check to prevent errors
    var datamapElement = document.getElementById("world-datamap");
    if (datamapElement) {
        var i = new Datamap({
            scope: "world",
            element: datamapElement,
            responsive: !0,
            geographyConfig: {
                popupOnHover: !1,
                highlightOnHover: !1,
                borderColor: "transparent",
                borderWidth: 1,
                highlightBorderWidth: 3,
                highlightFillColor: "rgba(0,123,255,0.5)",
                highlightBorderColor: "transparent",
                borderWidth: 1
            },
            bubblesConfig: {
                popupTemplate: function(e, i) {
                    return '<div class="datamap-sales-hover-tooltip">' + i.country + '<span class="ml-2"></span>' + i.sold + "</div>"
                },
                borderWidth: 0,
                highlightBorderWidth: 0,
                highlightFillColor: "rgb(255, 255, 255)",
                highlightBorderColor: "rgb(255, 255, 255)",
                fillOpacity: .75
            },
            fills: {
                Visited: "#777",
                neato: "#777",
                white: "#777",
                defaultFill: "#EBEFF2"
            }
        });
        
        i.bubbles([{
            centered: "USA",
            fillKey: "white",
            radius: 5,
            sold: "$500",
            country: "United States"
        }, {
            centered: "SAU",
            fillKey: "Visited",
            radius: 5,
            sold: "$900",
            country: "Saudia Arabia"
        }, {
            centered: "RUS",
            fillKey: "neato",
            radius: 5,
            sold: "$250",
            country: "Russia"
        }, {
            centered: "CAN",
            fillKey: "white",
            radius: 5,
            sold: "$1000",
            country: "Canada"
        }, {
            centered: "IND",
            fillKey: "Visited",
            radius: 5,
            sold: "$50",
            country: "India"
        }, {
            centered: "AUS",
            fillKey: "white",
            radius: 5,
            sold: "$700",
            country: "Australia"
        }, {
            centered: "BGD",
            fillKey: "Visited",
            radius: 5,
            sold: "$1500",
            country: "Bangladesh"
        }])
    }

})(jQuery);

(function($) {
    "use strict"

     // LINE CHART
      // Morris bar chart
 var morrisBarElement = document.getElementById('morris-bar-chart');
 if (morrisBarElement) {
     Morris.Bar({
        element: 'morris-bar-chart',
        data: [{
            y: '2016',
            a: 100,
            b: 90,
        }, {
            y: '2017',
            a: 75,
            b: 65,
        }, {
            y: '2018',
            a: 50,
            b: 40,
        }, {
            y: '2019',
            a: 75,
            b: 65,
        }, {
            y: '2020',
            a: 50,
            b: 40,
        }, {
            y: '2021',
            a: 75,
            b: 65,
        }, {
            y: '2022',
            a: 100,
            b: 90,
        }],
        xkey: 'y',
        ykeys: ['a', 'b', 'c'],
        labels: ['A', 'B', 'C'],
        barColors: ['#FC6C8E', '#7571f9'],
        hideHover: 'auto',
        gridLineColor: 'transparent',
        resize: true
    });
 }

})(jQuery);


(function($) {
    "use strict"


    var todoListElement = document.getElementById('todo_list');
    if (todoListElement) {
        $('#todo_list').slimscroll({
            position: "right",
            size: "5px",
            height: "250px",
            color: "transparent"
        });
    }

    var activityElement = document.getElementById('activity');
    if (activityElement) {
        $('#activity').slimscroll({
            position: "right",
            size: "5px",
            height: "390px",
            color: "transparent"
        });
    }

})(jQuery);



(function($) {
    "use strict"

    let chartWidget2Element = document.getElementById("chart_widget_2");
    if (chartWidget2Element) {
        chartWidget2Element.height = 280;
        new Chart(chartWidget2Element, {
            type: 'line',
            data: {
                labels: ["2010", "2011", "2012", "2013", "2014", "2015", "2016"],
                type: 'line',
                defaultFontFamily: 'Montserrat',
                datasets: [{
                    data: [0, 15, 57, 12, 85, 10, 50],
                    label: "iPhone X",
                    backgroundColor: '#847DFA',
                    borderColor: '#847DFA',
                    borderWidth: 0.5,
                    pointStyle: 'circle',
                    pointRadius: 5,
                    pointBorderColor: 'transparent',
                    pointBackgroundColor: '#847DFA',
                }, {
                    label: "Pixel 2",
                    data: [0, 30, 5, 53, 15, 55, 0],
                    backgroundColor: '#F196B0',
                    borderColor: '#F196B0',
                    borderWidth: 0.5,
                    pointStyle: 'circle',
                    pointRadius: 5,
                    pointBorderColor: 'transparent',
                    pointBackgroundColor: '#F196B0',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, 
                tooltips: {
                    mode: 'index',
                    titleFontSize: 12,
                    titleFontColor: '#000',
                    bodyFontColor: '#000',
                    backgroundColor: '#fff',
                    titleFontFamily: 'Montserrat',
                    bodyFontFamily: 'Montserrat',
                    cornerRadius: 3,
                    intersect: false,
                },
                legend: {
                    display: false, 
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        fontFamily: 'Montserrat',
                    },
                },
                scales: {
                    xAxes: [{
                        display: true,
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        scaleLabel: {
                            display: false,
                            labelString: 'Month'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Value'
                        }
                    }]
                },
                title: {
                    display: false,
                }
            }
        });
    }

})(jQuery);

(function($) {
    "use strict"

    let chartWidget3Element = document.getElementById("chart_widget_3");
    if (chartWidget3Element) {
        chartWidget3Element.height = 130;
        new Chart(chartWidget3Element, {
            type: 'line',
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                type: 'line',
                defaultFontFamily: 'Montserrat',
                datasets: [{
                    data: [0, 15, 57, 12, 85, 10],
                    label: "iPhone X",
                    backgroundColor: 'transparent',
                    borderColor: '#847DFA',
                    borderWidth: 2,
                    pointStyle: 'circle',
                    pointRadius: 5,
                    pointBorderColor: '#847DFA',
                    pointBackgroundColor: '#fff',
                }]
            },
            options: {
                responsive: !0,
                maintainAspectRatio: true,
                tooltips: {
                    mode: 'index',
                    titleFontSize: 12,
                    titleFontColor: '#fff',
                    bodyFontColor: '#fff',
                    backgroundColor: '#000',
                    titleFontFamily: 'Montserrat',
                    bodyFontFamily: 'Montserrat',
                    cornerRadius: 3,
                    intersect: false,
                },
                legend: {
                    display: false,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        fontFamily: 'Montserrat',
                    },
                },
                scales: {
                    xAxes: [{
                        display: false,
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        scaleLabel: {
                            display: false,
                            labelString: 'Month'
                        }
                    }],
                    yAxes: [{
                        display: false,
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        scaleLabel: {
                            display: true,
                            labelString: 'Value'
                        }
                    }]
                },
                title: {
                    display: false,
                }
            }
        });
    }

})(jQuery);



/*******************
Chart Chartist
*******************/
(function($) {
    "use strict"

    var chartWidget3Element = document.querySelector("#chart_widget_3");
    if (chartWidget3Element) {
        new Chartist.Line("#chart_widget_3", {
            labels: ["1", "2", "3", "4", "5", "6", "7", "8"],
            series: [
                [4, 5, 1.5, 6, 7, 5.5, 5.8, 4.6]
            ]
        }, {
            low: 0,
            showArea: !1,
            showPoint: !0,
            showLine: !0,
            fullWidth: !0,
            lineSmooth: !1,
            chartPadding: {
                top: 4,
                right: 4,
                bottom: -20,
                left: 4
            },
            axisX: {
                showLabel: !1,
                showGrid: !1,
                offset: 0
            },
            axisY: {
                showLabel: !1,
                showGrid: !1,
                offset: 0
            }
        });
    }

    var chartWidget31Element = document.querySelector("#chart_widget_3_1");
    if (chartWidget31Element) {
        new Chartist.Pie("#chart_widget_3_1", {
            series: [35, 65]
        }, {
            donut: !0,
            donutWidth: 10,
            startAngle: 0,
            showLabel: !1
        });
    }

})(jQuery);




/*******************
Pignose Calender
*******************/
(function ($) {
    "use strict";

    var yearCalendarElement = document.querySelector(".year-calendar");
    if (yearCalendarElement) {
        $(".year-calendar").pignoseCalendar({
            theme: "blue"
        });
    }
    
    var calendarInput = document.querySelector("input.calendar");
    if (calendarInput) {
        $("input.calendar").pignoseCalendar({
            format: "YYYY-MM-DD"
        });
    }

})(jQuery);