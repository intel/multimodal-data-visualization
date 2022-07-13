import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import ReplayIcon from '@mui/icons-material/Replay';

function Visualization() {
	const [runnningPipeline, setRunnningPipeline] = useState([]);
	const [noPipelineRunningError, setNoPipelineRunningError] = useState(false);
	const [baseUrl, setBaseUrl] = useState(
		`http://${window.location.hostname}:8080/`
	);
	const [runningPipelineUrl, setRunningPipelineUrl] = useState(
		`http://${window.location.hostname}:8082/`
	);

	useEffect(() => {
		getRunningPipelines();
		return () => {
			setRunnningPipeline([]);
		};
	}, []);

	// get running pipeline state
	const getRunningPipelines = () => {
		setRunnningPipeline([]);
		axios
			.get(`${baseUrl}pipelines/status`)
			.then((response) => {
				const data = response.data.filter((e) => {
					return e.state === 'RUNNING';
				});
				if (data && data.length) {
					data.map((e) => {
						getPeerId(e.id);
					});
					setNoPipelineRunningError(false);
				} else {
					setNoPipelineRunningError(true);
				}
			})
			.catch((error) => {
				console.log('There was an error!', error);
			});
	};

	// get peer id of running pipeline
	const getPeerId = (id) => {
		axios
			.get(`${baseUrl}pipelines/${id}`)
			.then((response) => {
				const peer_id = response.data.request.destination.frame['peer-id'];
				const data = {
					url: `${runningPipelineUrl}?destination_peer_id=${peer_id}&instance_id=${id}`,
					id: peer_id,
				};
				setRunnningPipeline((prevArr) => [...prevArr, data]);
			})
			.catch((error) => {
				console.log('There was an error!', error);
			});
	};

	return (
		<div>
			<Box sx={{ flexGrow: 1 }}>
				<AppBar position='static'>
					<Toolbar>
						<Typography variant='h4' sx={{ flexGrow: 1 }}>
							Visualization
						</Typography>
						<Button
							variant='contained'
							className='reload_button'
							color='secondary'
							onClick={getRunningPipelines}
						>
							<ReplayIcon color='inherit' />
						</Button>
					</Toolbar>
				</AppBar>
			</Box>
			{noPipelineRunningError ? (
				<Alert severity='error' color='error'>
					There is currently no pipeline running !
				</Alert>
			) : (
				<div className='videoDiv'>
					<Grid
						container
						spacing={2}
						direction='row'
						justify='flex-start'
						alignItems='flex-start'
					>
						{runnningPipeline.map((el) => (
							<Grid
                  item
                  xs={12}
                  sm={runnningPipeline.length === 1 ? 12 : 6}
                  md={
                      runnningPipeline.length === 1
                          ? 12
                          : runnningPipeline.length === 2
                          ? 6
                          : 4
                  }
                  key={el.id}
                >
								<Card className='card'>
									<CardHeader className='stream_card_heading' title={el.id} />
									<CardContent>
										<iframe
											className={
                                    runnningPipeline.length === 1
                                        ? 'stream_card_lg'
                                        : runnningPipeline.length === 2
                                        ? 'stream_card_md'
                                        : 'stream_card_sm'
                                }
											scrolling='no'
											src={el.url}
											title={el.id}
										></iframe>
									</CardContent>
								</Card>
							</Grid>
						))}
					</Grid>
				</div>
			)}
		</div>
	);
}

export default Visualization;
