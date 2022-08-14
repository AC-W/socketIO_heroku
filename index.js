const socket = io("https://socketioserveracw.herokuapp.com");
// const socket = io("http://127.0.0.1:8000");


socket.on('connect', () => {
    console.log('connected')
    // socket.emit("server_reset")
    socket.emit('login',{user_ID:'admin',password:'admin'})
    // socket.emit('create_account',{new_user_ID:'ACW',new_username:'Ryan Wei',password:'GGG'})
    socket.emit('join_game',{game_ID:'test2',join_as:'spectate'})
    socket.emit('new_message',{game_ID:'test2',message:'hi'})
    // socket.emit('get_server_status')
})

socket.on('disconnect', () => {
    console.log('disconnect')
})

socket.on('logged in', (data) =>{
    user_ID = data.user_ID
    username = data.username
    password = data.password
    console.log(username)
})

socket.on('success', (data) =>{
    console.log(data.msg)
})

socket.on('error', (data) =>{
    console.log(data.msg)
})

socket.on('server_status',(data) =>{
    console.log(data.client_count)
})

socket.on('update_state',(data) =>{
    console.log(data)
})

socket.on('update_chat',(data) =>{
    console.log(data)
})