import "./App.css";
import "./App.jsx"; 

function Result(){

    const fetchNumber = async () => {
		const responseNum = await fetch ("/api/response");
		if (!responseNum.ok){
			throw new Error();
		}
		const resultNum = await responseNum.json();
		setScore(resultNum)
	}

	const progressBar = ({currentValue, maxValue = 100}) => {
		return (<progress value={currentValue} max = {maxValue}></progress>)}

	useEffect(() => {
    	fetchNumber(); }, []);

    return (
        <div>
            <div>
                <img src ={resumeLogo} className="logo resume" alt="Resume logo" />

                <h1>ResuMatch</h1>
            </div>
            <div>
                    {progressBar({currentValue: matchScore, maxValue: 100 })}
            </div>
        </div>
    )
}