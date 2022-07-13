import Visualization from './components/Visualization';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import './App.css';

const theme = createTheme({
	palette: {
		primary: {
			main: '#2196f3',
		},
		secondary: {
			main: '#f44336',
		},
	},
	components: {
		MuiButton: {
			styleOverrides: {
				root: {
					fontSize: '1rem',
				},
			},
		},
	},
});

function App() {
	return (
		<ThemeProvider theme={theme}>
			<div className='App'>
				<Visualization />
			</div>
		</ThemeProvider>
	);
}

export default App;
