package components

import (
	"fmt"
	"crypto/rand"
)

func GenerateSessionToken() (string, error, bool) {
	tokenString := rand.Text()

	if tokenString == "" {
		return "", fmt.Errorf("Error Generating Random Token"), false
	}

	return tokenString, nil, true
}
