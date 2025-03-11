package login

import (
	//"net/http"
	//"context"
	"fmt"
	"net/http"

	//"github.com/jackc/pgx/v5/pgxpool"
	//dbconn "github.com/vchen7629/cyphria/login-api/internal/db_connection"
)

type LoginCredentials struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func Login() (bool, error) {
	//var loginsuccess bool
	fmt.Println("Hello From create new User\n")

	/*err := dbconn.DBConn.QueryRow(context.Background(), `

	`).Scan(&loginsuccess)*/

	/*if err != nil {
		
	}*/
	return true, nil
}

func LoginHandler(w http.ResponseWriter, r *http.Request) {

}