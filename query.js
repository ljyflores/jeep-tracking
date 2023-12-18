// Copyright 2019 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

'use strict';

function main() {
    // [START bigquery_query]
    // [START bigquery_client_default_credentials]
    // Import the Google Cloud client library using default credentials
    const {BigQuery} = require('@google-cloud/bigquery');
    const bigquery = new BigQuery();
    // [END bigquery_client_default_credentials]
    async function query() {

        const query = `SELECT agg.table.* 
        FROM (SELECT stop_id, ARRAY_AGG(STRUCT(table) 
        ORDER BY insertion_time DESC)[SAFE_OFFSET(0)] agg 
        FROM \`eco-folder-402813.jeep_etas.test\` table 
        GROUP BY stop_id)`;

        // For all options, see https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs/query
        const options = {
            query: query,
            // Location must match that of the dataset(s) referenced in the query.
            location: 'US',
            projectId: 'eco-folder-402813'
        };

        // Run the query as a job
        const [job] = await bigquery.createQueryJob(options);
        console.log(`Job ${job.id} started.`);

        // Wait for the query to finish
        const [rows] = await job.getQueryResults();

        // Print the results
        // console.log('Rows:');
        // rows.forEach(row => console.log(row));
        console.log(`Job ${job.id} finished.`)
        return rows
    }
    // [END bigquery_query]
    query();
}
main();