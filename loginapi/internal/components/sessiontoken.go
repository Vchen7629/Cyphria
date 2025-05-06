package components

import (
	"fmt"
	"crypto/rand"
)

func GenerateSessionToken() (string, error) {
	tokenString := rand.Text()

	if tokenString == "" {
		return "", fmt.Errorf("Error Generating Random Token")
	}

	return tokenString, nil
}
