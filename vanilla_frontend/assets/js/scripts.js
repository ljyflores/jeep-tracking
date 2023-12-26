data = {
  AL1: {
    stopName: "5th Ave corner 72nd",
    buses: [
      {
        route: "Aurora Loop",
        busID: "PRG 356",
        eta: "5 mins",
        location: "Broadway corner Church Ave",
      },
      {
        route: "Downtown Express",
        busID: "FRD 902",
        eta: "10 mins",
        location: "5th Ave, Near Metropolitan Theater",
      },
      {
        route: "Seaside Drive",
        busID: "TRL 463",
        eta: "15 mins",
        location: "4 Privet Drive",
      },
    ],
  },
  AL2: {
    stopName: "8th Ave corner 55th",
    buses: [
      {
        route: "Uptown Circuit",
        busID: "KLM 125",
        eta: "3 mins",
      },
      {
        route: "Airport Line",
        busID: "XYZ 784",
        eta: "7 mins",
      },
    ],
  },
  AL3: {
    stopName: "Broadway corner 42nd",
    buses: [
      {
        route: "Midtown Direct",
        busID: "ABC 123",
        eta: "2 mins",
      },
      {
        route: "Harbor Route",
        busID: "DEF 456",
        eta: "20 mins",
      },
      {
        route: "Parkside Shuttle",
        busID: "GHI 789",
        eta: "10 mins",
      },
      {
        route: "University Link",
        busID: "JKL 012",
        eta: "30 mins",
      },
    ],
  },
};

const sample_data = [
    {
      "f": [
        {
          "v": "AL3"
        },
        {
          "v": "ID1,ID2,ID3"
        },
        {
          "v": "Atok Street,Atok Street,Atok Street"
        },
        {
          "v": "12040.5,12040.5,12040.5"
        },
        {
          "v": "ABC12345,DEF67890,GHI12345"
        },
        {
          "v": "2023-12-20 22:26:10"
        }
      ]
    },
    {
      "f": [
        {
          "v": "AL2"
        },
        {
          "v": "ID1,ID2,ID3"
        },
        {
          "v": "Atok Street,Atok Street,Atok Street"
        },
        {
          "v": "6505.3,6505.3,6505.3"
        },
        {
          "v": "ABC12345,DEF67890,GHI12345"
        },
        {
          "v": "2023-12-20 22:26:10"
        }
      ]
    },
    {
      "f": [
        {
          "v": "AL4"
        },
        {
          "v": "ID1,ID2,ID3"
        },
        {
          "v": "Atok Street,Atok Street,Atok Street"
        },
        {
          "v": "12170,12170,12170"
        },
        {
          "v": "ABC12345,DEF67890,GHI12345"
        },
        {
          "v": "2023-12-20 22:26:10"
        }
      ]
    },
    {
      "f": [
        {
          "v": "AL5"
        },
        {
          "v": "ID1,ID2,ID3"
        },
        {
          "v": "Atok Street,Atok Street,Atok Street"
        },
        {
          "v": "12170,12170,12170"
        },
        {
          "v": "ABC12345,DEF67890,GHI12345"
        },
        {
          "v": "2023-12-20 22:26:10"
        }
      ]
    },
    {
      "f": [
        {
          "v": "AL1"
        },
        {
          "v": "ID1,ID2,ID3"
        },
        {
          "v": "Atok Street,Atok Street,Atok Street"
        },
        {
          "v": "3563.6,3563.6,3563.6"
        },
        {
          "v": "ABC12345,DEF67890,GHI12345"
        },
        {
          "v": "2023-12-20 22:26:10"
        },
        {
          "v": "Aurora Loop, Aurora Loop, Aurora Loop"
        },
        {
          "v": "a,b,c;d,e,f;g,h,i"
        },
      ]
    }
  ]

// find list that is stop id of current site
// for each bus
// once we find the right bus id
// we use the next object to create a list of bus objects
// [{id: ID1}, {}, {}]
// [{id: ID1, location: Atok Street, ETA: 3563.6, plate: ABC}]
// then we iterate through this list of objects to produce the website
//
//
// how to handle errors?
// e.g. missing entries etc. then just put [NOT FOUND]
// e.g. bus ID not found? then just put Invalid Bus ID

// function queryWorkers() {
//   // [START bigquery_query]
//   // [START bigquery_client_default_credentials]
//   // Import the Google Cloud client library using default credentials
//   const output = fetch('https://jeep-tracking-worker.ljyflores.workers.dev/query').then(res => res.json());
//   return output
// }

function processBusData(data, currentStopID) {
    // Initialize an empty array to hold bus objects
    let busList = [];
    console.log("Within processBusData function");
    console.log(data);
    // Loop through each bus entry in the data
    data.forEach(entry => {
        console.log(entry);

        // Destructure the array to access elements easily
        const [stopID, ids, locations, etas, plates, times] = entry.f.map(item => item.v);
        // const [stopID, ids, locations, etas, plates, times, routeNames, nextStops] = entry.f.map(item => item.v);

        if (stopID == currentStopID) {
            // Split the string values to arrays
            const idArray = ids.split(',');
            const locationArray = locations.split(',');
            const etaArray = etas.split(',');
            const plateArray = plates.split(',');
            // const routeNameArray = routeNames.split(',');
            // const nextStopArray = nextStops.split(';');


            // Construct bus objects and add them to busList
            for (let i = 0; i < idArray.length; i++) {
                busList.push({
                    id: idArray[i],
                    location: locationArray[i],
                    eta: Math.round(parseFloat(etaArray[i]) / 60),
                    plate: plateArray[i],
                    routeName: "Aurora Loop",
                    nextStopList: ["current stop", "next stop"]
                    // routeName: routeNameArray[i],
                    // nextStopList: nextStopArray[i].split(",")
                });
            }
        }
    });

    // Return the list of bus objects
    return busList;
}

function stopListHTML(stopList) {
    html = ``
    for (let i = 0; i < stopList.length; i++) {
        if (i == 0) {
            html += `<li class="fw-bold">
                <div class="row align-items-center w-100">
                <div class="col">${stopList[i]}</div></div>
            </li>`

        } else {
            html += `<li>
                <div class="row align-items-center w-100">
                <div class="col">${stopList[i]}</div>
            </div></li>`
        }
    }
    return `<ul>${html}</ul>`
}

$(document).ready(async function () {
  // const fetchData = function(callback) {
  //     $.getJSON('data/bus-data.json', callback);
  // };

  $("#goButton").click(function () {
    const stopID = $("#stopID").val().trim().toUpperCase();
    if (stopID) {
      window.location.href = "stops.html?stop=" + stopID;
    } else {
      alert("Please input a valid Stop ID.");
    }
  });

  if (window.location.pathname.includes("stops")) {
    const params = new URLSearchParams(window.location.search);
    const stopID = params.get("stop");
    let sample_data2 = await fetch('https://jeep-tracking-worker.ljyflores.workers.dev/query').then(res => res.json());
    const processedBuses = processBusData(sample_data2.rows, stopID);
    console.log(processedBuses);
    if (data[stopID]) {
      $("#currentStop").text(data[stopID].stopName);
      processedBuses.forEach((bus, index) => {
        $("#busDetails").append(
            ` <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button ${
                    index != 0 ? "collapsed" : ""
                    } w-100" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${index.toString()}" aria-expanded="true" aria-controls="collapse-${index.toString()}">

                    <div class="row align-items-center w-100">
                        <div class="col">
                            <div class="vstack">
                                <div class="p-2 fw-bold">${bus.routeName}</div>
                                <div class="p-2">${bus.plate}</div>
                            </div>
                        </div>
                        <div class="col text-end">
                            <div class="vstack">
                                <div class="p-2">
                                    <strong>ETA</strong>: ${bus.eta} min. &nbsp; &nbsp;
                                </div>
                                <div class="p-2" style="font-size: 14px;">
                                    ${bus.location} &nbsp; &nbsp;
                                </div>
                            </div>
                        </div>
                    </div>
                </button>
                </h2>
                <div id="collapse-${index.toString()}"
                    class="accordion-collapse collapse ${index == 0 ? "show" : ""}"
                    data-bs-parent="#accordionExample">
                    <div class="accordion-body">
                        ${stopListHTML(bus.nextStopList)}
                    </div>
                </div>
            </div>
            `
        );
      });
    } else {
      $("#busDetails").text("No buses found for this stop.");
    }
  }
});
