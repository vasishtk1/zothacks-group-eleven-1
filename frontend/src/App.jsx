import { useState } from "react";

import "./App.css";
import resumeLogo from "./assets/resumeLogo.svg"
import React from "react";

/*
This is the starting point of our application. Here, we can begin coding 
and transforming this page into whatever best suits our needs. 
For example, we can start by creating a login page, home page, or an about section; 
there are many ways to get your application up and running. 
With App.jsx, we can also define global variables and routes to store information as well as page navigation.
*/
function App() {
	const [file, setFile] = useState(null); 
	const [uploadStatus, setUploadStatus] = useState("");

	const handleFileChange = (event) => {
		setFile(event.target.files[0]);
	};

	const handleUpload = async (event) => {
		event.preventDefault();
		if (!file) {
			alert("Please select a PDF file first!");
			return;
		}

		const formData = new FormData();
		formData.append("file", file);

		try {
			const response = await fetch("/api/upload", {
				method: "POST",
				body: formData,
			});

			if (!response.ok) throw new Error("Upload failed");

			const data = await response.json();
			console.log("Upload success:", data);
			setUploadStatus(`Uploaded ${data.filename} (${data.size} bytes)`);
		} catch (error) {
			console.error("Error uploading file:", error);
			setUploadStatus("Error uploading file");
		}
	};

	const fetchNumber = async () => {
		const responseNum = await fetch ("/api/response");
		if (!responseNum.ok){
			throw new Error();
		}
		const resultNum = await responseNum.json();
		return (resultNum)
	}

	const progressBar = ({currentValue, maxValue = 100}) => {
		return (<progress value={currentValue} max = {maxValue}></progress>)
	}

	return (
		<div className = "app-container">
			<div>
				<img src ={resumeLogo} className="logo resume" alt="Resume logo" />
			</div>

			<h1>ResuMatch</h1>

			<p>
				Welcome to ResuMatch, your AI-powered resume analyzer! <br />
				Upload your resume as a PDF or DOCX, and we'll evaluate its effectiveness. <br />
				Receive personalized feedback and actionable suggestions to enhance your resume, ensuring it stands out to potential employers. <br />
				Start optimizing your career prospects with ResuMatch today!
			</p>
		
			<div className="App">
				<form>
					<h2>Resume File Upload</h2>
					<input 
						type="file" 
						accept=".pdf,.doc,.docx"
						onChange={handleFileChange}/>
					<button onClick={handleUpload} type="submit">Upload</button>
				</form>
				<p>{uploadStatus}</p>
			</div>

			<div className = "ScoreBar">
				matchScore = {fetchNumber}
				progressBar(matchScore)
			</div>
		</div>
	)}

export default App;
