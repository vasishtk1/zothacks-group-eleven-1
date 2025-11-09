import React, { useState, useEffect } from "react";

import "./App.css";
import resumeLogo from "./assets/resumeLogo.svg"
import Markdown from "react-markdown";
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
	const [textContent, setTextContent] = useState("");
	const [matchScore, setScore] = useState(0)
	const [suggestions, setSuggestions] = useState("")
	const [toRender, setToRender] = useState(false)
	const [load, setLoad] = useState(false)

	const handleFileChange = (event) => {
	setFile(event.target.files[0]);
	};

	const handleSubmit = async (event) => {
		event.preventDefault();
	
		if (!file) {
			alert("Please select a resume file first!");
			return;
		}
	
		if (!textContent.trim()) {
			alert("Please enter a job description!");
			return;
		}
	
		const formData = new FormData();
		formData.append("file", file, file.name);
		formData.append("job_description", textContent);



		for (const [k, v] of formData.entries()) {
			console.log(k, v instanceof File ? v.name : v);
		}

		console.log(file, textContent, formData)
	
		try {
			setLoad(true)

			//asend both file and description to backend
			const response = await fetch("/api/upload", {
				method: "POST",
				body: formData,
			});
			setLoad(false)
	
			if (!response.ok) throw new Error("Upload failed");
	
			const data = await response.json();
			console.log("Upload success:", data);

			setScore(data["Score: "])
			setSuggestions(data["Suggestions: "])
			setToRender(true)
		} catch (error) {
			console.error("Error uploading:", error);
			setUploadStatus("Error uploading file or description");
		}
	};

	const progressBar = ({ currentValue, maxValue = 100 }) => {
		const percent = Math.min((currentValue / maxValue) * 100, 100);
	
		return (
			<div className="progress-container">
				<div className="progress-bar" style={{ width: `${percent}%` }}>
					<span className="progress-text">{Math.round(percent)}%</span>
				</div>
			</div>
		);
	};
	
	if (load == true){
		return(
		<div className ="loading-screen">
			<div>
				<img src ={resumeLogo} className="logo resume" alt="Resume logo" />
				<h1>ResuMatch</h1>
			</div>
			<div>
				<h2>We are loading your resume compatibility score!</h2>
				
				<h2>loading...</h2>
			</div>
		</div>
		)
	}
	else if (toRender == false) {
		return (
			<div className = "app-container">
				<div>
					<img src ={resumeLogo} className="logo resume" alt="Resume logo" />
				</div>

				<h1>ResuMatch</h1>

				<p>
					Welcome to ResuMatch, your AI-powered resume analyzer! <br />
					Upload your resume as a PDF or DOCX along with the job description, and we'll evaluate its effectiveness. <br />
					Receive personalized feedback and actionable suggestions to enhance your resume, ensuring it's compatibility for your employer! '. <br />
					Start optimizing your career prospects with ResuMatch today!
				</p>
				
				<div className="App">
					{
					<form onSubmit={handleSubmit}>
						<h2>Enter Job Description</h2>
							<div className="job-input">
								<label htmlFor="job-description"></label>
								<textarea
									id="job-description"
									value={textContent}
									onChange={e => setTextContent(e.target.value)}
								/>
							</div>

						<h2>Resume File Upload</h2>
							<input
								type="file"
								accept=".pdf,.doc,.docx"
								onChange={handleFileChange}
							/>
						<button type="submit">Analyze Resume</button>
					</form>
					}
					<p>{uploadStatus}</p>
				</div>
			</div>
		)
	} 
	
	else if (toRender == true) {
		return (
			<div className = "app-container">
				<div>
					<img src ={resumeLogo} className="logo resume" alt="Resume logo" />

					<h1>ResuMatch</h1>
				</div>
				<div>
					<h2>Your match!</h2>
					{progressBar({currentValue: matchScore, maxValue: 100 })}
					<h2>Percent Score {matchScore}%</h2>
				</div>
				<div className="suggestions-container">
					<h2 style={{ textAlign: "center", marginBottom: "1rem" }}>
						Our Suggestions for You:
					</h2>
					<Markdown>{suggestions}</Markdown>
				</div>
			</div>
		)
	};
}

export default App;
