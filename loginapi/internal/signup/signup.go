package signup

import (
	//"net/http"
	"fmt"
	"net/http"
)

type SignUpUserInfo struct {
	Username string `json:"username"`
	Email string `json:"email"`
	Password string `json:"password"`
}

type SignUpHandler interface {
	CreateNewUser()
}

func CreateNewUser(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Hello from create new user")
}