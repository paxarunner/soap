# soap
SOAP Request сервис слушает на порту 6767 и при передаче ИИН, выбирает из базы информацию, генерирует XML, отдает пользователю.
Без авторизации.
Пример запроса:

<soap11env:Envelope xmlns:soap11env="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hey="spyne.soap">
<soap11env:Header/>
<soap11env:Body>
<hey:soap>
<hey:iin>780917402089</hey:iin>
</hey:soap>
</soap11env:Body>
</soap11env:Envelope>
