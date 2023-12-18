import { Router } from 'itty-router';

// function query_bigquery() {

// 	// [START bigquery_query]
// 	// [START bigquery_client_default_credentials]
// 	// Import the Google Cloud client library using default credentials

// 	// const {BigQuery} = require('@google-cloud/bigquery');
// 	// const bigquery = new BigQuery();

// 	// [END bigquery_client_default_credentials]
// 	async function query() {
  
// 		// const query = `SELECT agg.table.*
// 		// FROM (SELECT stop_id, ARRAY_AGG(STRUCT(table) 
// 		// ORDER BY insertion_time DESC)[SAFE_OFFSET(0)] agg 
// 		// FROM \`eco-folder-402813.jeep_etas.test\` table 
// 		// GROUP BY stop_id)`;
	
// 		// // For all options, see https://cloud.google.com/bigquery/docs/reference/rest/v2/jobs/query
// 		// const options = {
// 		// 	query: query,
// 		// 	// Location must match that of the dataset(s) referenced in the query.
// 		// 	location: 'US',
// 		// 	projectId: 'eco-folder-402813'
// 		// };
	
// 		// // Run the query as a job
// 		// const [job] = await bigquery.createQueryJob(options);
// 		// console.log(`Job ${job.id} started.`);
	
// 		// // Wait for the query to finish
// 		// const [rows] = await job.getQueryResults();
	
// 		// // Print the results
// 		// // console.log('Rows:');
// 		// // rows.forEach(row => console.log(row));
// 		// console.log(`Job ${job.id} finished.`)
// 		// return rows
// 		return {"a":"Hello from the inside!"}
// 	}
// 	// [END bigquery_query]
// 	const query_output = query(); 
// 	return query_output;
//   }


// now let's create a router (note the lack of "new")
const router = Router();

// // Jeep tracking queries
// router.get('/query', () => new Response(handleRequest()));

// GET collection index
router.get('/api/todos', () => new Response('Todos Index!'));

// GET item
router.get('/api/todos/:id', ({ params }) => new Response(`Todo #${params.id}`));

// POST to the collection (we'll use async here)
router.post('/api/todos', async (request) => {
	const content = await request.json();

	return new Response('Creating Todo: ' + JSON.stringify(content));
});

// 404 for everything else
router.all('*', () => new Response('Not Found.', { status: 404 }));

export default router;