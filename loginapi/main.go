package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
    "syscall"
	"context"
	"github.com/gorilla/mux"
	"github.com/Vchen7629/Cyphria/loginapi/config/middleware"
	"github.com/Vchen7629/Cyphria/loginapi/config/postgres"
	"github.com/Vchen7629/Cyphria/loginapi/config/redis"
	"github.com/Vchen7629/Cyphria/loginapi/internal/accountComponents"
	"github.com/Vchen7629/Cyphria/loginapi/internal/authenticatedRequests"
)

func RouteHandlers(r *mux.Router) {
	r.HandleFunc("/", helloWorld)
	r.HandleFunc("/login", accountComponents.LoginHandler).Methods(http.MethodPost, http.MethodOptions)
	r.HandleFunc("/logout", accountComponents.LogoutHandler).Methods(http.MethodPost, http.MethodOptions)
	r.HandleFunc("/signup",  accountComponents.SignUpHandler).Methods(http.MethodPost, http.MethodOptions)
	r.HandleFunc("/getuserdata", authenticatedRequests.FetchUserDataHandler).Methods(http.MethodPost, http.MethodOptions)
	http.Handle("/", r)
}

func main(){
	r := mux.NewRouter()
	LoadEnvFile()
	postgres.PoolConfig()
	postgres.Main()
	redisClient.GetRedisClient()
	RouteHandlers(r)
	
	corsRouter := middleware.CorsMiddleware(r)
	srv := &http.Server {
		Handler: corsRouter,
		Addr: "0.0.0.0:3000",
	}
	
	// go channel to listen for os quit command
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)

	go func() {
		<-quit 
		log.Println("Shutting down Server")

		err := srv.Shutdown(context.Background())

		if err != nil {
			log.Fatalf("Error Shutting Down Server: %s", err)
		}

		postgres.DBConn.Close()
	}()

	err := srv.ListenAndServe() 
	
	if err != nil && err != http.ErrServerClosed {
		log.Fatalf("ListenAndServe(): %s", err)
	}
}

func helloWorld(w http.ResponseWriter, r *http.Request) {
	fmt.Printf("Hello from golang api!\n")
}