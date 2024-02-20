import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { KafkaProducerService } from '../kafka-producer/kafka-producer.service';

@Injectable()
export class StorageJSONService {
  constructor(
    private kafkaService: KafkaProducerService,
    private configService: ConfigService,
  ) {}
  private KAFKA_TOPIC_NAME = this.configService.get(
    'kafka.defaultTopicNames.saveOfJSON',
  );

  public saveJSON(data: JSON) {
    const record = this.kafkaService.createRecord(this.KAFKA_TOPIC_NAME, [
      JSON.stringify(data),
    ]);
    const [key] = this.kafkaService.produce(record);
    return key;
  }
}
