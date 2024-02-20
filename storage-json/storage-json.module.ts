import { Module } from '@nestjs/common';
import { StorageJSONController } from './storage-json.controller';
import { StorageJSONService } from './storage-json.service';
import { KafkaProducerModule } from '../kafka-producer/kafka-producer.module';

@Module({
  imports: [KafkaProducerModule],
  controllers: [StorageJSONController],
  providers: [StorageJSONService],
})
export class StorageJSONModule {}
