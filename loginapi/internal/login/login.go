package login

import (
	//"net/http"
	"fmt"
	"net/http"
)

type LoginCredentials struct {
	Username string `json:"username"`
	Password string `json:"password"`
}


func Login(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Hello From create new User\n")
}