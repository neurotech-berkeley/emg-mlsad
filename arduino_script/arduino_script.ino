#define A0  26
#define A1  25
#define A2  34
#define A3  39
#define A4  36

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  while(!Serial);
}
void loop() {
  Serial.print(0);
  Serial.print(" ");
  Serial.print(4096);
  Serial.print(" ");
  // Serial.print(millis());
  // Serial.print(" ");
  Serial.print(hallRead());
  Serial.print(" ");
  Serial.println(analogRead(A0));
  Serial.print(" ");
  // Serial.print(analogRead(A1));
  // Serial.print(" ");
  // Serial.print(analogRead(A2));
  // Serial.print(" ");
  // Serial.print(analogRead(A3));
  // Serial.print(" ");
  // Serial.println(analogRead(A4));
  delay(1);
}
