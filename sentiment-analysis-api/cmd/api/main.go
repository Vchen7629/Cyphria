package main

import (
    "fmt"
    "github.com/jonreiter/govader"
)

func main() {
	analyzer := govader.NewSentimentIntensityAnalyzer()
	sentiment := analyzer.PolarityScores("I'm 22 years old,studying computer engineering and I'm seriously concerned about the rapid advancement of AI and its impact on the industry. Would it be wise to switch to electrical engineering or another field of engineering? I'd appreciate any insights!")

	fmt.Println("Compound score:", sentiment.Compound)
	fmt.Println("Positive score:", sentiment.Positive)
	fmt.Println("Neutral score:", sentiment.Neutral)
	fmt.Println("Negative score:", sentiment.Negative)
}