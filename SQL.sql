SELECT activities_data.ticket_id, 
	MAX(CASE(status)
		WHEN "Open" THEN (strftime('%s', activities_data.performed_at) - strftime('%s', r.minstart_at)) / 3600
		ELSE 0 
		END) AS time_spent_open,
	MAX(CASE(status)
		WHEN "Waiting for Customer" THEN (strftime('%s', activities_data.performed_at) - strftime('%s', r.minstart_at)) / 3600 
		ELSE 0
		END) AS time_spent_waiting_on_customer,
	MAX(CASE(status)
		WHEN "Pending" THEN (strftime('%s', activities_data.performed_at) - strftime('%s', r.minstart_at)) / 3600
		ELSE 0
		END) AS time_spent_waiting_for_response,
	MAX(CASE(status)
		WHEN "Resolved" THEN (strftime('%s', activities_data.performed_at) - strftime('%s', r.minstart_at)) / 3600 
		ELSE 0  
		END) AS time_till_resolution,
	MIN((strftime('%s', activities_data.performed_at) - strftime('%s', r.minstart_at)) / 3600) AS time_to_first_response 
	FROM
	(
		SELECT Min(start_at) as minstart_at, metadata_id
		FROM metadata
		GROUP BY metadata_id
	) r
JOIN activities_data ON r.metadata_id = activities_data.metadata_id
JOIN activity a ON a.ticket_id = activities_data.ticket_id
WHERE a.status IS NOT NULL
GROUP BY activities_data.ticket_id
ORDER BY activities_data.ticket_id DESC