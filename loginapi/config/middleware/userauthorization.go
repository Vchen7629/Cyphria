package middleware

import (
	"net/http"
	"github.com/golang-jwt/jwt"
)

type UserInfo struct {
	UserId string
	Username string
}

type Claims struct {
	*jwt.StandardClaims
	TokenType string
	UserInfo
}


func VerifyJWT(w http.ResponseWriter) {
	/*tokenString := "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmb28iOiJiYXIiLCJleHAiOjE1MDAwLCJpc3MiOiJ0ZXN0In0.HE7fK0xOQwFEr4WDgRWj4teRPZ6i3GLwD5YCm6Pwu_c"

	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		return []byte("AllYourBase"), nil
	})
	if err != nil {
		http.Error(w, "Invalid token", http.StatusUnauthorized)
	}

	claims, ok := token.Claims.(*Claims)
	if !ok || !token.Valid {
		http.Error(w, "Invalid token claims", http.StatusUnauthorized)
		return
	}*/

}