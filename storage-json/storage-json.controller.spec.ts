import { Test, TestingModule } from '@nestjs/testing';
import { StorageJSONController } from './storage-json.controller';
import { KafkaProducerModule } from '../kafka-producer/kafka-producer.module';
import { ConfigModule } from '@nestjs/config';
import configuration from '../app/app.configuration';
import { StorageJSONModule } from './storage-json.module';
import { StorageJSONService } from './storage-json.service';

describe('StorageJSONController', () => {
  let controller: StorageJSONController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [
        ConfigModule.forRoot({
          isGlobal: true,
          load: [configuration],
        }),
        KafkaProducerModule,
        StorageJSONModule,
      ],
      controllers: [StorageJSONController],
      providers: [StorageJSONService],
    }).compile();

    controller = module.get<StorageJSONController>(StorageJSONController);
  });

  it('should be defined', () => {
    expect(controller).toBeDefined();
  });
});
