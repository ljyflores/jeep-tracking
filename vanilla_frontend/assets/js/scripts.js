data = {
    "AL1": {
        "stopName": "5th Ave corner 72nd",
        "buses": [
            {
                "route": "Aurora Loop",
                "busID": "PRG 356",
                "eta": "5 mins",
                "location": "Broadway corner Church Ave"
            },
            {
                "route": "Downtown Express",
                "busID": "FRD 902",
                "eta": "10 mins",
                "location": "5th Ave, Near Metropolitan Theater"
            },
            {
                "route": "Seaside Drive",
                "busID": "TRL 463",
                "eta": "15 mins",
                "location": "4 Privet Drive"
            }
        ]
    },
    "AL2": {
        "stopName": "8th Ave corner 55th",
        "buses": [
            {
                "route": "Uptown Circuit",
                "busID": "KLM 125",
                "eta": "3 mins"
            },
            {
                "route": "Airport Line",
                "busID": "XYZ 784",
                "eta": "7 mins"
            }
        ]
    },
    "AL3": {
        "stopName": "Broadway corner 42nd",
        "buses": [
            {
                "route": "Midtown Direct",
                "busID": "ABC 123",
                "eta": "2 mins"
            },
            {
                "route": "Harbor Route",
                "busID": "DEF 456",
                "eta": "20 mins"
            },
            {
                "route": "Parkside Shuttle",
                "busID": "GHI 789",
                "eta": "10 mins"
            },
            {
                "route": "University Link",
                "busID": "JKL 012",
                "eta": "30 mins"
            }
        ]
    }
};



$(document).ready(function() {
    // const fetchData = function(callback) {
    //     $.getJSON('data/bus-data.json', callback);
    // };

    $('#goButton').click(function() {
        const stopID = $('#stopID').val().trim().toUpperCase();
        if(stopID) {
            window.location.href = "stops.html?stop=" + stopID;
        } else {
            alert('Please input a valid Stop ID.');
        }
    });

    if (window.location.pathname.includes('stops.html')) {
        const params = new URLSearchParams(window.location.search);
        const stopID = params.get('stop');

        if(data[stopID]) {
            $('#currentStop').text(data[stopID].stopName);
            data[stopID].buses.forEach((bus, index) => {
                $('#busDetails').append(
                    `
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                        <button class="accordion-button ${ (index != 0) ? 'collapsed' : '' } w-100" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${index.toString()}" aria-expanded="true" aria-controls="collapse-${index.toString()}">

                            <div class="row align-items-center w-100">
                            <div class="col">
                            <div class="vstack">
                            <div class="p-2 fw-bold">${bus.route}</div>
                            <div class="p-2">${bus.busID}</div>
                            </div>
                            </div>
                            <div class="col text-end">
                            <div class="vstack">
                            <div class="p-2">
                            <strong>ETA</strong>: ${bus.eta} &nbsp; &nbsp;
                            </div>
                            <div class="p-2" style="font-size: 12px;">
                            ${bus.location} &nbsp; &nbsp;
                            </div>
                            </div>
                            </div>
                            </div>
                        </button>
                        </h2>
                        <div id="collapse-${index.toString()}" class="accordion-collapse collapse ${ (index == 0) ? 'show' : '' }" data-bs-parent="#accordionExample">
                        <div class="accordion-body">
                        <ul>
                        <li class="fw-bold">
                            <div class="row align-items-center w-100">
                            <div class="col">5th Ave corner 72nd</div>
                            <div class="col text-end">(AL1)</div>
                        </div>
                        </li>
                        <li>
                            <div class="row align-items-center w-100">
                            <div class="col">5th Ave corner 72nd</div>
                            <div class="col text-end">(AL1)</div>
                        </div>
                        </li>
                        </ul>

                        </div>
                        </div>
                    </div>
                    `

                    // `<div class="card mb-3">
                    //     <div class="card-header" id="heading${index}">
                    //         <h5 class="mb-0">
                    //             <button class="btn btn-link" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${index}" aria-expanded="true" aria-controls="collapse${index}">
                    //                 Route: ${bus.route}
                    //             </button>
                    //         </h5>
                    //     </div>
                    //     <div id="collapse${index}" class="collapse" aria-labelledby="heading${index}">
                    //         <div class="card-body">
                    //             <strong>Bus ID:</strong> ${bus.busID}<br>
                    //             <strong>ETA:</strong> ${bus.eta}<br>
                    //         </div>
                    //     </div>
                    // </div>`
                );
            });
        } else {
            $('#busDetails').text("No buses found for this stop.");
        }    }
});
