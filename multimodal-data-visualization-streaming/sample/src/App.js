import { useState } from 'react';
import './App.css';

function App() {
	const defaultUrl =
		'https://github.com/intel-iot-devkit/sample-videos/blob/master/person-bicycle-car-detection.mp4?raw=true';
	const [inputUrl, setInputUrl] = useState(defaultUrl);
	const [streamUrl, setStreamUrl] = useState(defaultUrl);

	const handleChange = (value) => {
		setInputUrl(value);
	};

	const handleSubmit = () => {
		setStreamUrl(inputUrl);
	};

	return (
		<div className='container-fluid'>
			<div className='mt-2 mb-3 row'>
				<div className='col-8'>
					<input
						type='url'
						value={inputUrl}
						onChange={(e) => handleChange(e.target.value)}
						className='form-control'
						id='inputPassword'
					/>
				</div>
				<div className='col-2'>
					<button
						type='submit'
						className='btn btn-primary'
						onClick={handleSubmit}
					>
						Stream
					</button>
				</div>
			</div>

			<video
				className='stream'
				id='stream'
				key={streamUrl}
				autoplay='autoplay'
				muted='muted'
				loop='loop'
				playsinline='playsinline'
				preload='metadata'
				data-aos='fade-up'
			>
				<source src={streamUrl} type='video/mp4' />
				Your browser does not support HTML video.
			</video>
		</div>
	);
}

export default App;
