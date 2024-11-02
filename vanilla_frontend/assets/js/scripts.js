data = {
  AL1: {
    stopName: "Plaza Principal",
    buses: [
      {
        route: "Ruta A - Centro",
        busID: "PRG 356",
        eta: "5 mins",
        location: "Avenida Central",
      },
      {
        route: "Expreso Centro",
        busID: "FRD 902", 
        eta: "10 mins",
        location: "Calle Comercio",
      },
      {
        route: "Circular Centro",
        busID: "TRL 463",
        eta: "15 mins",
        location: "Plaza Mayor",
      },
    ],
  },
  AL2: {
    stopName: "Mercado Central",
    buses: [
      {
        route: "Ruta A - Centro",
        busID: "KLM 125",
        eta: "3 mins",
        location: "Avenida Comercial",
      },
      {
        route: "Expreso Mercado",
        busID: "XYZ 784",
        eta: "7 mins",
        location: "Calle Principal",
      },
    ],
  },
  AL3: {
    stopName: "Hospital General",
    buses: [
      {
        route: "Ruta A - Centro",
        busID: "ABC 123",
        eta: "2 mins",
        location: "Avenida Salud",
      },
      {
        route: "Expreso Hospital",
        busID: "DEF 456",
        eta: "20 mins",
        location: "Calle Medicina",
      },
      {
        route: "Circular Hospital",
        busID: "GHI 789",
        eta: "10 mins",
        location: "Plaza Salud",
      },
    ],
  },
  BL1: {
    stopName: "Campus Principal",
    buses: [
      {
        route: "Ruta B - Universidad",
        busID: "UNI 101",
        eta: "4 mins",
        location: "Entrada Principal",
      },
      {
        route: "Expreso Campus",
        busID: "EDU 202",
        eta: "12 mins",
        location: "Avenida Universidad",
      },
    ],
  },
  BL2: {
    stopName: "Biblioteca Central",
    buses: [
      {
        route: "Ruta B - Universidad",
        busID: "LIB 303",
        eta: "6 mins",
        location: "Plaza Biblioteca",
      },
      {
        route: "Circular Universidad",
        busID: "STU 404",
        eta: "15 mins",
        location: "Calle Estudios",
      },
    ],
  },
  BL3: {
    stopName: "Residencias Estudiantiles",
    buses: [
      {
        route: "Ruta B - Universidad",
        busID: "DOR 505",
        eta: "8 mins",
        location: "Bloque Residencial",
      },
      {
        route: "Expreso Residencias",
        busID: "RES 606",
        eta: "18 mins",
        location: "Avenida Estudiantes",
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
          "v": "Avenida Salud,Calle Medicina,Plaza Salud"
        },
        {
          "v": "12040.5,12040.5,12040.5"
        },
        {
          "v": "ABC123,DEF456,GHI789"
        },
        {
          "v": "2023-12-20 22:26:10"
        },
        {
          "v": "Ruta A - Centro,Expreso Hospital,Circular Hospital"
        },
        {
          "v": "a,b,c;d,e,f;g,h,i"
        }
      ]
    },
    {
      "f": [
        {
          "v": "BL1"
        },
        {
          "v": "ID4,ID5"
        },
        {
          "v": "Entrada Principal,Avenida Universidad"
        },
        {
          "v": "6505.3,6505.3"
        },
        {
          "v": "UNI101,EDU202"
        },
        {
          "v": "2023-12-20 22:26:10"
        },
        {
          "v": "Ruta B - Universidad,Expreso Campus"
        },
        {
          "v": "x,y,z;p,q,r"
        }
      ]
    },
    {
      "f": [
        {
          "v": "BL2"
        },
        {
          "v": "ID6,ID7"
        },
        {
          "v": "Plaza Biblioteca,Calle Estudios"
        },
        {
          "v": "12170,12170"
        },
        {
          "v": "LIB303,STU404"
        },
        {
          "v": "2023-12-20 22:26:10"
        },
        {
          "v": "Ruta B - Universidad,Circular Universidad"
        },
        {
          "v": "m,n,o;j,k,l"
        }
      ]
    },
    {
      "f": [
        {
          "v": "BL3"
        },
        {
          "v": "ID8,ID9"
        },
        {
          "v": "Bloque Residencial,Avenida Estudiantes"
        },
        {
          "v": "12170,12170"
        },
        {
          "v": "DOR505,RES606"
        },
        {
          "v": "2023-12-20 22:26:10"
        },
        {
          "v": "Ruta B - Universidad,Expreso Residencias"
        },
        {
          "v": "u,v,w;r,s,t"
        }
      ]
    },
    {
      "f": [
        {
          "v": "AL1"
        },
        {
          "v": "ID10,ID11,ID12"
        },
        {
          "v": "Avenida Central,Calle Comercio,Plaza Mayor"
        },
        {
          "v": "3563.6,3563.6,3563.6"
        },
        {
          "v": "PRG356,FRD902,TRL463"
        },
        {
          "v": "2023-12-20 22:26:10"
        },
        {
          "v": "Ruta A - Centro,Expreso Centro,Circular Centro"
        },
        {
          "v": "a,b,c;d,e,f;g,h,i"
        }
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

function processBusData(data, currentStopID) {
    // Initialize an empty array to hold bus objects
    let busList = [];
    console.log("Within processBusData function");
    console.log(data);
    // Loop through each bus entry in the data
    data.forEach(entry => {
        console.log(entry);

        // Destructure the array to access elements easily
        //const [stopID, ids, locations, etas, plates, times] = entry.f.map(item => item.v);
        const [stopID, ids, locations, etas, plates, times, stopName, routeNames, nextStops] = entry.f.map(item => item.v);

        if (stopID == currentStopID) {
            // Split the string values to arrays
            const idArray = ids.split(',');
            const locationArray = locations.split(',');
            const etaArray = etas.split(',');
            const plateArray = plates.split(',');
            const routeNameArray = routeNames.split(',');
            const nextStopArray = nextStops.split(';');

            // Construct bus objects and add them to busList
            for (let i = 0; i < idArray.length; i++) {
                busList.push({
                    id: idArray[i],
                    location: locationArray[i],
                    eta: Math.round(parseFloat(etaArray[i]) / 60),
                    plate: plateArray[i],
                    // routeName: "Aurora Loop",
                    // nextStopList: ["current stop", "next stop"]
                    routeName: routeNameArray[i],
                    nextStopList: nextStopArray[i].split(",")
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
      if (processedBuses.length > 0) {
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
        // Use the static data when no real-time data is available
        data[stopID].buses.forEach((bus, index) => {
          $("#busDetails").append(
            ` <div class="accordion-item">
                <h2 class="accordion-header">
                    <button class="accordion-button ${
                    index != 0 ? "collapsed" : ""
                    } w-100" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${index.toString()}" aria-expanded="true" aria-controls="collapse-${index.toString()}">

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
                        <ul><li>Next stops information not available</li></ul>
                    </div>
                </div>
            </div>
            `
          );
        });
      }
    } else {
      $("#busDetails").text("No buses found for this stop.");
    }
  }
});
