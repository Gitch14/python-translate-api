import { Test, TestingModule } from '@nestjs/testing';
import { StorageJSONService } from './storage-json.service';
import { ConfigModule } from '@nestjs/config';
import configuration from '../app/app.configuration';
import { KafkaProducerModule } from '../kafka-producer/kafka-producer.module';

describe('StorageJSONService', () => {
  let service: StorageJSONService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [
        ConfigModule.forRoot({
          isGlobal: true,
          load: [configuration],
        }),
        KafkaProducerModule,
      ],
      providers: [StorageJSONService],
    }).compile();

    service = module.get<StorageJSONService>(StorageJSONService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });
});
