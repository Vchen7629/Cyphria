package logout

import (
	"fmt"
	"net/http"
)

func Logout(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Hello from logout!\n")
}