SELECT activities_data.ticket_id, 
	/* Get Open status and check time open */
	MAX(CASE WHEN status = "Open" THEN (strftime('%s', activities_data.performed_at) - strftime('%s', min_response.minstart_at)) / 3600 ELSE 0 END) AS time_spent_open,
	/* Get Waiting for Customer status and check time waiting */
	MAX(CASE WHEN status = "Waiting for Customer" THEN (strftime('%s', activities_data.performed_at) - strftime('%s', min_response.minstart_at)) / 3600 ELSE 0 END) AS time_spent_waiting_on_customer,
	/* Get Pending status and check time pending */
	MAX(CASE WHEN status = "Pending" THEN (strftime('%s', activities_data.performed_at) - strftime('%s', min_response.minstart_at)) / 3600 ELSE 0 END) AS time_spent_waiting_for_response,
	/* Get Resolved status and check time */
	MAX(CASE WHEN status = "Resolved" THEN (strftime('%s', activities_data.performed_at) - strftime('%s', min_response.minstart_at)) / 3600 ELSE 0 END) AS time_till_resolution,
	/* Get earliest response time and check first time of activity */
	MIN((strftime('%s', activities_data.performed_at) - strftime('%s', min_response.minstart_at)) / 3600) AS time_to_first_response 
	FROM
	(
		SELECT Min(start_at) as minstart_at, metadata_id
		FROM metadata
		GROUP BY metadata_id
	) min_response	
JOIN activities_data ON min_response.metadata_id = activities_data.metadata_id
JOIN activity a ON a.ticket_id = activities_data.ticket_id
WHERE a.status IS NOT NULL
GROUP BY activities_data.ticket_id
ORDER BY activities_data.ticket_id DESC